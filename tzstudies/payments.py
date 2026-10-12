"""Payments are confirmed only by authenticated provider queries, never a redirect."""

import copy
import hashlib
import re
import secrets
import uuid
from datetime import timedelta

import click
from flask import current_app
from flask_login import current_user
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tzstudies.extensions import db
from tzstudies.payment_config import amount, money_text
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent, utcnow
from tzstudies.paypal import GatewayError, PayPal, binding, provider_identifier

WEBHOOK_EVENTS = frozenset(
    (
        "PAYMENT.CAPTURE.COMPLETED",
        "PAYMENT.CAPTURE.PENDING",
        "PAYMENT.CAPTURE.DECLINED",
        "PAYMENT.CAPTURE.REFUNDED",
        "PAYMENT.CAPTURE.REVERSED",
    )
)


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
        if (
            content["user"] != current_user.id
            or content["plan"] != plan_id
            or not re.fullmatch(r"[a-f0-9]{48}", content["nonce"])
        ):
            raise ValueError
    except (BadSignature, KeyError, TypeError, ValueError):
        raise ValueError("Invalid checkout intent") from None
    return hashlib.sha256(token.encode()).hexdigest()


def create_order(plan_id, plan, intent_key):
    existing = db.session.scalar(select(PaymentOrder).where(PaymentOrder.intent_key == intent_key))
    if existing:
        return existing, False

    identifier = uuid.uuid4().hex
    order = PaymentOrder(
        id=identifier,
        order_reference="TZ" + identifier.upper(),
        user_id=current_user.id,
        intent_key=intent_key,
        plan_id=plan_id,
        plan_name=plan["name"],
        plan_snapshot=copy.deepcopy(plan),
        amount=amount(plan["price"]),
        currency=plan["currency"],
        status="creating",
        provider="paypal",
        provider_mode=current_app.config["PAYPAL_MODE"],
    )
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


def paypal_order(order):
    if order.provider != "paypal" or order.provider_mode != current_app.config["PAYPAL_MODE"]:
        raise ConfirmationError("Order provider or environment mismatch")


def verified_record(order, data, capture=None):
    """Validate the immutable local snapshot against authenticated PayPal responses."""
    paypal_order(order)
    try:
        if (
            not isinstance(data, dict)
            or not provider_identifier(data.get("id"))
            or order.provider_id
            and data["id"] != order.provider_id
            or data.get("intent") != "CAPTURE"
            or data.get("status")
            not in ("CREATED", "SAVED", "APPROVED", "PAYER_ACTION_REQUIRED", "COMPLETED", "VOIDED")
            or amount(order.plan_snapshot["price"]) != order.amount
            or order.plan_snapshot["currency"] != order.currency
        ):
            raise ValueError
        units = data["purchase_units"]
        if not isinstance(units, list) or len(units) != 1:
            raise ValueError
        unit = units[0]
        if (
            unit.get("reference_id") != order.id
            or unit.get("custom_id") != binding(order)
            or unit.get("invoice_id") != order.order_reference
        ):
            raise ValueError
        money_text(order.amount, order.currency)
        total = unit["amount"]
        if amount(total["value"]) != order.amount or total["currency_code"] != order.currency:
            raise ValueError
        items = unit["items"]
        if (
            len(items) != 1
            or items[0].get("sku") != order.plan_id
            or items[0].get("name") != order.plan_name
            or items[0].get("quantity") != "1"
            or items[0].get("category") != "DIGITAL_GOODS"
            or amount(items[0]["unit_amount"]["value"]) != order.amount
            or items[0]["unit_amount"]["currency_code"] != order.currency
        ):
            raise ValueError
        captures = unit.get("payments", {}).get("captures", [])
        if not isinstance(captures, list) or len(captures) > 1:
            raise ValueError
        if not captures:
            if capture or data["status"] == "COMPLETED":
                raise ValueError
            return None
        linked = captures[0]
        record = capture or linked
        if (
            not provider_identifier(record.get("id"))
            or record["id"] != linked.get("id")
            or order.payment_reference
            and record["id"] != order.payment_reference
            or record.get("status")
            not in ("COMPLETED", "PENDING", "DECLINED", "FAILED", "REFUNDED", "PARTIALLY_REFUNDED")
            or amount(record["amount"]["value"]) != order.amount
            or record["amount"]["currency_code"] != order.currency
            or record.get("final_capture") is not True
        ):
            raise ValueError
        related = record.get("supplementary_data", {}).get("related_ids", {})
        if related.get("order_id", data["id"]) != data["id"]:
            raise ValueError
        if record.get("invoice_id", order.order_reference) != order.order_reference or record.get(
            "custom_id", binding(order)
        ) != binding(order):
            raise ValueError
        if record["status"] == "COMPLETED" and data["status"] != "COMPLETED":
            raise ValueError
        return record
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ConfirmationError("Provider order, product or capture does not match") from None


def _apply_locked(store, order, data, capture=None, event=None, refund=None):
    record = verified_record(order, data, capture)
    if event and store.get(PaymentWebhookEvent, event["id"]):
        return "duplicate"
    now = utcnow()
    if record:
        status = record["status"]
        if event and event["provider_id"] != record["id"]:
            raise ConfirmationError("Webhook capture does not belong to this order")
        if event and event["event"] == "PAYMENT.CAPTURE.REFUNDED":
            try:
                if (
                    not refund
                    or refund["status"] != "COMPLETED"
                    or refund["id"] != event["resource_id"]
                    or refund["amount"]["currency_code"] != order.currency
                    or not 0 < amount(refund["amount"]["value"]) <= order.amount
                    or status not in ("REFUNDED", "PARTIALLY_REFUNDED")
                ):
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                raise ConfirmationError("Refund not confirmed") from None
        elif (
            event
            and event["event"] == "PAYMENT.CAPTURE.COMPLETED"
            and status not in ("COMPLETED", "REFUNDED", "PARTIALLY_REFUNDED")
        ):
            raise ConfirmationError("Capture not yet completed")
        if event and event["event"] == "PAYMENT.CAPTURE.REVERSED":
            status = "REVERSED"  # Signature verified; capture identity and amount queried above.
        order.payment_reference = record["id"]
        terminal = order.status in ("refunded", "partially_refunded", "reversed")
        if status in ("REFUNDED", "PARTIALLY_REFUNDED", "REVERSED"):
            if order.status != "reversed" and not (order.status == "refunded" and status == "PARTIALLY_REFUNDED"):
                order.status = status.lower()
                order.refunded_at = order.refunded_at or now
                order.provider_status = status
            order.checkout_url = None
        elif status == "COMPLETED" and not terminal:
            if not order.completed_at:
                order.completed_at = now
                order.status = "paid"
            order.provider_status = status
            order.checkout_url = None
        elif not order.completed_at and not terminal:
            order.status = "processing" if status == "PENDING" else "failed"
            order.provider_status = status
    elif not order.completed_at and order.status not in ("refunded", "partially_refunded", "reversed", "cancelled"):
        order.status = "failed" if data["status"] == "VOIDED" else "pending"
        order.provider_status = data["status"]
    order.last_checked_at = now
    order.updated_at = now
    if event:
        if not record:
            raise ConfirmationError("Missing webhook capture")
        store.add(
            PaymentWebhookEvent(
                id=event["id"],
                order_id=order.id,
                event=event["event"],
                provider_id=event["provider_id"],
                received_at=now,
                processed_at=now,
            )
        )
    return "processed"


def apply_confirmation(order_id, data, capture=None, event=None, refund=None):
    with Session(db.engine) as store, store.begin():
        order = store.scalar(select(PaymentOrder).where(PaymentOrder.id == order_id).with_for_update())
        if not order:
            raise ConfirmationError("Order not found")
        return _apply_locked(store, order, data, capture, event, refund)


def confirm_order(order, event=None):
    paypal_order(order)
    gateway = current_app.extensions["paypal"]
    data = gateway.get_order(order.provider_id)
    linked = verified_record(order, data)
    capture = gateway.get_capture(linked["id"]) if linked else None
    refund = (
        gateway.get_refund(event["resource_id"]) if event and event["event"] == "PAYMENT.CAPTURE.REFUNDED" else None
    )
    return apply_confirmation(order.id, data, capture, event, refund)


def capture_payment(identifier):
    """A row lock serializes captures. PayPal request IDs also protect network retries."""
    gateway = current_app.extensions["paypal"]
    error = None
    with Session(db.engine) as store, store.begin():
        order = store.scalar(select(PaymentOrder).where(PaymentOrder.id == identifier).with_for_update())
        if not order or order.user_id != current_user.id:
            raise ConfirmationError("Order owner mismatch")
        paypal_order(order)
        if order.completed_at or order.status in ("refunded", "partially_refunded", "reversed", "cancelled", "failed"):
            return "unchanged"
        data = gateway.get_order(order.provider_id)
        linked = verified_record(order, data)
        if linked:
            return _apply_locked(store, order, data, gateway.get_capture(linked["id"]))
        if not current_app.config["PAYMENTS_ENABLED"] or data["status"] != "APPROVED":
            raise ConfirmationError("Payment is paused or awaiting approval")
        if order.capture_requested_at and utcnow() - order.capture_requested_at > timedelta(hours=5):
            raise ConfirmationError("Capture outcome needs manual reconciliation")
        order.capture_requested_at = order.capture_requested_at or utcnow()
        order.status = "processing"
        try:
            response = gateway.capture_order(order)
            if not isinstance(response, dict) or response.get("id") != order.provider_id:
                raise ConfirmationError("Capture order ID mismatch")
            # Capture responses can omit item metadata; query the complete order.
            data = gateway.get_order(order.provider_id)
            linked = verified_record(order, data)
            if not linked:
                raise ConfirmationError("Capture has not been confirmed")
            _apply_locked(store, order, data, gateway.get_capture(linked["id"]))
        except (GatewayError, ConfirmationError) as exc:
            # Commit the uncertain attempt; subsequent requests query before retrying
            # with the same request ID, and never retry beyond PayPal's retention window.
            error = exc
    if error:
        raise error
    return "processed"


def init_payments(app):
    app.extensions["paypal"] = PayPal(app.config)

    @app.cli.command("payments-check")
    def configuration_check():
        """Read-only readiness checks. No API calls, tokens or connection URLs printed."""
        from sqlalchemy import inspect, text

        from tzstudies.extensions import limiter

        click.echo("Payment provider: PayPal " + app.config["PAYPAL_MODE"])
        for key in ("PAYMENTS_ENABLED", "PAYMENT_TEST_PLAN_ENABLED"):
            click.echo(key + ": " + str(app.config[key]))
        for key in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET", "PAYPAL_WEBHOOK_ID", "OPENAI_API_KEY"):
            click.echo(key + ": " + ("configured" if app.config.get(key) else "missing"))
        click.echo("Return URL: " + app.config["PAYMENT_RETURN_URL"])
        click.echo("Webhook URL: " + app.config["PAYPAL_WEBHOOK_URL"])
        columns = {c["name"] for c in inspect(db.engine).get_columns("payment_order")}
        click.echo(
            "Payment schema ready: "
            + str({"provider", "provider_mode", "refunded_at", "capture_requested_at"}.issubset(columns))
        )
        click.echo("Database connectivity: " + str(db.session.scalar(text("SELECT 1")) == 1))
        try:
            click.echo("Rate limit storage connectivity: " + str(limiter.storage.check()))
        except Exception:
            click.echo("Rate limit storage connectivity: False")
        click.echo(
            "Historical provider orders preserved: "
            + str(db.session.query(PaymentOrder).filter(PaymentOrder.provider != "paypal").count())
        )

    @app.cli.command("payments-reconcile")
    @click.option("--order", "reference", required=True)
    def reconcile(reference):
        """Authenticated read-only reconciliation; never creates/captures payments."""
        order = db.session.scalar(select(PaymentOrder).where(PaymentOrder.order_reference == reference))
        if not order:
            raise click.ClickException("Order not found.")
        try:
            confirm_order(order)
        except (GatewayError, ConfirmationError, IntegrityError):
            db.session.rollback()
            raise click.ClickException("Payment could not be confirmed. Legacy orders remain archived.") from None
        click.echo("PayPal order checked. No charge was initiated.")
