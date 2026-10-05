"""Payments are confirmed only by authenticated provider queries, never a redirect."""

import copy
import hashlib
import re
import secrets
import uuid

import click
from flask import current_app
from flask_login import current_user
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tzstudies.clickpesa import ClickPesa, GatewayError
from tzstudies.extensions import db
from tzstudies.payment_config import amount
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent, utcnow

SUCCESS = {"SUCCESS", "SETTLED"}
KNOWN_STATUSES = SUCCESS | {"PENDING", "PROCESSING", "FAILED", "ON-HOLD", "REFUNDED", "REVERSED"}


class ConfirmationError(Exception):
    pass


def _signer():
    return URLSafeTimedSerializer(current_app.secret_key, salt="tz-payment-intent-v1")


def new_intent(plan_id):
    return _signer().dumps({"user": current_user.id, "plan": plan_id, "nonce": secrets.token_hex(24)})


def read_intent(token, plan_id):
    if not isinstance(token, str) or len(token) > 1024:
        raise ValueError("Invalid checkout intent")
    try:
        content = _signer().loads(token, max_age=current_app.config["PAYMENT_INTENT_TTL"])
        if content["user"] != current_user.id or content["plan"] != plan_id or not re.fullmatch(r"[a-f0-9]{48}", content["nonce"]):
            raise ValueError
    except (BadSignature, KeyError, TypeError, ValueError):
        raise ValueError("Invalid checkout intent") from None
    return hashlib.sha256(token.encode()).hexdigest()


def create_order(plan_id, plan, intent_key):
    existing = db.session.scalar(select(PaymentOrder).where(PaymentOrder.intent_key == intent_key))
    if existing:
        return existing, False
    identifier = uuid.uuid4().hex
    order = PaymentOrder(id=identifier, order_reference="TZ" + identifier.upper(), user_id=current_user.id,
                         intent_key=intent_key, plan_id=plan_id, plan_name=plan["name"],
                         plan_snapshot=copy.deepcopy(plan), amount=amount(plan["price"]), currency=plan["currency"], status="creating")
    db.session.add(order)
    try:
        db.session.commit()  # Durable order exists before any provider call.
        return order, True
    except IntegrityError:
        db.session.rollback()
        existing = db.session.scalar(select(PaymentOrder).where(PaymentOrder.intent_key == intent_key))
        if not existing:
            raise
        return existing, False


def _identifier(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[a-zA-Z0-9._:-]{1,160}", value))


def verified_record(order, records, event=None):
    """Only the authenticated query response supplies financial truth."""
    matches = []
    for record in records:
        if record.get("orderReference") != order.order_reference:
            continue
        if record.get("clientId") != current_app.config["CLICKPESA_CLIENT_ID"]:
            raise ConfirmationError("Application mismatch")
        if not _identifier(record.get("id")) or not isinstance(record.get("status"), str) or record["status"] not in KNOWN_STATUSES:
            raise ConfirmationError("Invalid payment record")
        if event and record["id"] != event["provider_id"]:
            continue
        if record["status"] in SUCCESS:
            try:
                if amount(record.get("collectedAmount")) != order.amount or record.get("collectedCurrency") != order.currency or not _identifier(record.get("paymentReference")):
                    raise ConfirmationError("Payment amount, currency or reference mismatch")
            except ValueError:
                raise ConfirmationError("Invalid collected amount") from None
        matches.append(record)
    if not matches:
        raise ConfirmationError("No matching provider confirmation")
    successes = [record for record in matches if record["status"] in SUCCESS]
    if len(successes) > 1:
        raise ConfirmationError("Multiple successful transactions require review")
    return successes[0] if successes else matches[-1]


def apply_confirmation(order_id, record, event=None):
    """Row lock + unique constraints make retries and parallel callbacks harmless."""
    with Session(db.engine) as store, store.begin():
        order = store.scalar(select(PaymentOrder).where(PaymentOrder.id == order_id).with_for_update())
        if order is None:
            raise ConfirmationError("Order no longer exists")
        if event and store.get(PaymentWebhookEvent, event["id"]):
            return "duplicate"
        # Revalidate against the locked order, even if catalogue prices changed.
        verified_record(order, [record], event)
        now = utcnow()
        status = record["status"]
        if status in SUCCESS:
            if order.provider_id and order.provider_id != record["id"]:
                raise ConfirmationError("Another transaction is already linked")
            if order.payment_reference and order.payment_reference != record["paymentReference"]:
                raise ConfirmationError("Payment reference changed")
            order.provider_id = record["id"]
            order.payment_reference = record["paymentReference"]
            # A success/settlement replay must never re-complete or grant twice.
            if not order.completed_at and order.status not in ("refunded", "reversed"):
                order.status = "paid"
                order.completed_at = now
            order.checkout_url = None
        elif status in ("REFUNDED", "REVERSED"):
            if order.provider_id and order.provider_id != record["id"]:
                raise ConfirmationError("Reversal transaction mismatch")
            order.status = status.lower()
            order.checkout_url = None
        elif order.completed_at is None and order.status not in ("refunded", "reversed"):
            order.status = {"PENDING": "pending", "PROCESSING": "pending", "ON-HOLD": "on_hold", "FAILED": "failed"}[status]
        if status in {"REFUNDED", "REVERSED"} or order.status not in ("refunded", "reversed") and (not order.completed_at or status in SUCCESS):
            order.provider_status = status
        order.last_checked_at = now
        order.updated_at = now
        if event:
            store.add(PaymentWebhookEvent(id=event["id"], order_id=order.id, event=event["event"], provider_id=event["provider_id"], received_at=now, processed_at=now))
    return "processed"


def confirm_order(order, event=None):
    records = current_app.extensions["clickpesa"].query_payment(order.order_reference)
    record = verified_record(order, records, event)
    if event and event["event"] == "PAYMENT RECEIVED" and record["status"] not in SUCCESS | {"REFUNDED", "REVERSED"}:
        raise ConfirmationError("Provider has not confirmed receipt yet")
    return apply_confirmation(order.id, record, event)


def init_payments(app):
    app.extensions["clickpesa"] = ClickPesa(app.config)

    @app.cli.command("payments-check")
    def configuration_check():
        """Print configuration readiness, never credentials; no live API requests."""
        click.echo("Payments enabled: " + str(app.config["PAYMENTS_ENABLED"]))
        for key in ("CLICKPESA_CLIENT_ID", "CLICKPESA_API_KEY", "OPENAI_API_KEY"):
            click.echo(key + ": " + ("configured" if app.config.get(key) else "missing"))
        click.echo("Return URL: " + app.config["PAYMENT_RETURN_URL"])
        click.echo("Webhook URL: " + app.config["CLICKPESA_WEBHOOK_URL"])
        click.echo("Checksum verification: " + ("required" if app.config["CLICKPESA_CHECKSUM_KEY"] else "authenticated query only"))
        click.echo("Catalogue plans: " + ", ".join(app.extensions["payment_catalog"]["plans"]))
        click.echo("Gateway account activation/KYC cannot be inferred from local configuration.")

    @app.cli.command("payments-reconcile")
    @click.option("--order", "reference", required=True, help="Internal TZ… order reference (not payment credentials).")
    def reconcile(reference):
        """Recover a missed callback using an authenticated, read-only provider query."""
        order = db.session.scalar(select(PaymentOrder).where(PaymentOrder.order_reference == reference))
        if not order:
            raise click.ClickException("Order not found.")
        try:
            confirm_order(order)
        except (GatewayError, ConfirmationError, IntegrityError):
            db.session.rollback()
            raise click.ClickException("Payment could not be confirmed; review the account and retry later.") from None
        click.echo("Order checked with ClickPesa. No new charge was initiated.")
