"""Private PayPal checkout, CSRF-protected captures and verified callbacks."""

import json
import re
from urllib.parse import parse_qs, urlsplit

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import inspect, select, update
from sqlalchemy.exc import SQLAlchemyError

from tzstudies.extensions import csrf, db, limiter
from tzstudies.payment_config import amount, plan_available
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent
from tzstudies.payments import (
    WEBHOOK_EVENTS,
    ConfirmationError,
    capture_payment,
    confirm_order,
    create_order,
    new_intent,
    read_intent,
    verified_record,
)
from tzstudies.paypal import GatewayError, provider_identifier, valid_checkout_url
from tzstudies.routes.admin import admin_required

payments_bp = Blueprint("payments", __name__)


def _owned_order(identifier, owner_only=False):
    if not re.fullmatch(r"[a-f0-9]{32}", identifier):
        abort(404)
    order = db.session.get(PaymentOrder, identifier)
    if not order or order.user_id != current_user.id and (owner_only or not current_user.is_admin):
        abort(404)
    return order


def _orders(admin=False):
    query = select(PaymentOrder).order_by(PaymentOrder.created_at.desc()).limit(50)
    if not admin:
        query = query.where(PaymentOrder.user_id == current_user.id)
    return db.session.scalars(query).all()


@payments_bp.after_app_request
def private_payment_responses(response):
    if request.endpoint and request.endpoint.startswith("payments."):
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


@payments_bp.get("/payments")
@login_required
def index():
    plans = current_app.extensions["payment_catalog"]["plans"]
    available = (
        {key: plan for key, plan in plans.items() if plan_available(plan, current_user)}
        if current_app.config["PAYMENTS_ENABLED"]
        else {}
    )
    return render_template(
        "payments/index.html", plans=available, intents={key: new_intent(key) for key in available}, orders=_orders()
    )


@payments_bp.get("/admin/payments")
@admin_required
def admin():
    plans = current_app.extensions["payment_catalog"]["plans"]
    columns = {column["name"] for column in inspect(db.engine).get_columns("payment_order")}
    try:
        storage_ready = bool(limiter.storage.check())
    except Exception:
        storage_ready = False
    return render_template(
        "payments/admin.html",
        plans=plans,
        intents={key: new_intent(key) for key in plans},
        orders=_orders(admin=True),
        enabled=current_app.config["PAYMENTS_ENABLED"],
        credentials_ready=all(current_app.config.get(key) for key in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET")),
        return_url=current_app.config["PAYMENT_RETURN_URL"],
        webhook_url=current_app.config["PAYPAL_WEBHOOK_URL"],
        webhook_ready=bool(current_app.config["PAYPAL_WEBHOOK_ID"]),
        mode=current_app.config["PAYPAL_MODE"],
        schema_ready={"provider", "provider_mode", "refunded_at", "capture_requested_at"}.issubset(columns),
        storage_ready=storage_ready,
        openai_ready=bool(current_app.config.get("OPENAI_API_KEY")),
    )


def _checkout_navigation(order):
    if (
        current_app.config["PAYMENTS_ENABLED"]
        and order.provider == "paypal"
        and order.provider_mode == current_app.config["PAYPAL_MODE"]
        and order.status == "pending"
        and valid_checkout_url(order.checkout_url, current_app.config["PAYPAL_MODE"])
    ):
        # A separate GET navigation avoids form-action CSP blocking a POST redirect to another origin.
        return render_template("payments/checkout.html", checkout_url=order.checkout_url, order=order)
    return redirect(url_for("payments.order_page", identifier=order.id), code=303)


@payments_bp.post("/payments/checkout/<plan_id>")
@login_required
@limiter.limit("10 per hour; 3 per minute")
def checkout(plan_id):
    plan = current_app.extensions["payment_catalog"]["plans"].get(plan_id)
    if not current_app.config["PAYMENTS_ENABLED"] or not plan or not plan_available(plan, current_user):
        abort(404)
    try:
        intent = read_intent(request.form.get("intent"), plan_id)
    except ValueError:
        abort(400, description="Checkout expired. Open the payment page and try again.")
    order, created = create_order(plan_id, plan, intent)
    session["payment_order"] = order.id
    if created:
        try:
            data = current_app.extensions["paypal"].create_checkout(order)
            if (
                not isinstance(data, dict)
                or not provider_identifier(data.get("id"))
                or data.get("status") not in ("CREATED", "PAYER_ACTION_REQUIRED")
            ):
                raise GatewayError("invalid_response")
            raw_links = data.get("links", [])
            if not isinstance(raw_links, list) or any(not isinstance(link, dict) for link in raw_links):
                raise GatewayError("invalid_response")
            links = [
                link
                for link in raw_links
                if link.get("rel") in ("payer-action", "approve") and link.get("method") == "GET"
            ]
            checkout_url = links[0].get("href") if len(links) == 1 else None
            if not valid_checkout_url(checkout_url, current_app.config["PAYPAL_MODE"]):
                raise GatewayError("invalid_response")
            if parse_qs(urlsplit(checkout_url).query).get("token") != [data["id"]]:
                raise GatewayError("invalid_response")
            # PayPal may return a minimal create representation. Persist its ID
            # before retrieving the complete order for snapshot validation.
            db.session.execute(
                update(PaymentOrder)
                .where(PaymentOrder.id == order.id, PaymentOrder.status == "creating")
                .values(provider_id=data["id"], provider_status=data["status"])
            )
            db.session.commit()
            verified_record(order, current_app.extensions["paypal"].get_order(data["id"]))
            # A fast webhook may have completed this order while checkout was being created.
            db.session.execute(
                update(PaymentOrder)
                .where(PaymentOrder.id == order.id, PaymentOrder.status == "creating")
                .values(
                    provider_id=data["id"], provider_status=data["status"], checkout_url=checkout_url, status="pending"
                )
            )
            db.session.commit()
        except (GatewayError, ConfirmationError):
            db.session.rollback()
            # A timeout could mean a checkout was created. Never automatically create it again.
            db.session.execute(
                update(PaymentOrder)
                .where(PaymentOrder.id == order.id, PaymentOrder.status == "creating")
                .values(status="checkout_unknown")
            )
            db.session.commit()
            flash(
                "Checkout could not be opened. Your order was saved. Check its status before trying another payment.",
                "warning",
            )
        db.session.expire_all()
    return _checkout_navigation(order)


@payments_bp.get("/payments/orders/<identifier>")
@login_required
def order_page(identifier):
    return render_template("payments/order.html", order=_owned_order(identifier), returned=False)


@payments_bp.get("/payments/orders/<identifier>/continue")
@login_required
def continue_checkout(identifier):
    return _checkout_navigation(_owned_order(identifier, owner_only=True))


@payments_bp.get("/payments/orders/<identifier>/status")
@login_required
def order_status(identifier):
    order = _owned_order(identifier)
    return jsonify(
        status=order.status, completed_at=order.completed_at.isoformat() + "Z" if order.completed_at else None
    )


@payments_bp.post("/payments/orders/<identifier>/check")
@login_required
@limiter.limit("6 per hour; 1 per minute")
def check_order(identifier):
    order = _owned_order(identifier)
    try:
        confirm_order(order)
        flash("Payment status checked with PayPal.", "success")
    except (GatewayError, ConfirmationError, SQLAlchemyError):
        db.session.rollback()
        flash(
            "Payment has not been confirmed. Please wait, then check again. Do not make another payment yet.", "warning"
        )
    return redirect(url_for("payments.order_page", identifier=order.id), code=303)


@login_required
def return_page():
    identifier = request.args.get("order") or session.get("payment_order")
    order = _owned_order(identifier, owner_only=True) if isinstance(identifier, str) else None
    token = request.args.get("token")
    if token and (
        not order or order.provider != "paypal" or not provider_identifier(token) or token != order.provider_id
    ):
        abort(400)
    cancelled = request.args.get("cancelled") == "1"
    # GET hints cannot mark an order paid or cancelled. All state changes use CSRF POSTs.
    approval = bool(
        order
        and token == order.provider_id
        and not cancelled
        and current_app.config["PAYMENTS_ENABLED"]
        and order.status in ("pending", "processing")
    )
    return render_template("payments/order.html", order=order, returned=True, approval=approval, cancelled=cancelled)


@payments_bp.post("/payments/orders/<identifier>/capture")
@login_required
@limiter.limit("10 per hour; 3 per minute")
def capture(identifier):
    order = _owned_order(identifier, owner_only=True)
    if not current_app.config["PAYMENTS_ENABLED"] or request.form.get("token") != order.provider_id:
        abort(400)
    try:
        capture_payment(order.id)
    except (GatewayError, ConfirmationError, SQLAlchemyError):
        db.session.rollback()
        flash("The payment is not confirmed yet. Check this order before trying another payment.", "warning")
    return redirect(url_for("payments.order_page", identifier=order.id), code=303)


@payments_bp.post("/payments/orders/<identifier>/cancel")
@login_required
def cancel(identifier):
    order = _owned_order(identifier, owner_only=True)
    db.session.execute(
        update(PaymentOrder)
        .where(
            PaymentOrder.id == order.id,
            PaymentOrder.status == "pending",
            PaymentOrder.capture_requested_at.is_(None),
            PaymentOrder.completed_at.is_(None),
        )
        .values(status="cancelled", checkout_url=None)
    )
    db.session.commit()
    return redirect(url_for("payments.order_page", identifier=order.id), code=303)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


@csrf.exempt
@limiter.limit("120 per minute")
def webhook():
    if not current_app.config.get("PAYPAL_WEBHOOK_ID"):
        return jsonify(error="Webhook verification is not configured"), 503
    if not request.is_json or request.content_length and request.content_length > 65536:
        return jsonify(error="Invalid notification"), 400
    try:
        body = request.get_data(cache=False)
        if len(body) > 65536:
            raise ValueError
        payload = json.loads(body, object_pairs_hook=_unique_object)
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("id"), str)
            or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", payload["id"])
            or not isinstance(payload.get("event_type"), str)
            or not isinstance(payload.get("resource"), dict)
        ):
            raise ValueError
    except (ValueError, TypeError, RecursionError):
        return jsonify(error="Invalid notification"), 400
    gateway = current_app.extensions["paypal"]
    try:
        if not gateway.verify_webhook(payload, request.headers, body):
            return jsonify(error="Invalid notification signature"), 403
    except GatewayError:
        return jsonify(error="Notification verification temporarily unavailable"), 503
    event_name = payload["event_type"]
    if event_name not in WEBHOOK_EVENTS:
        return "", 204
    if db.session.get(PaymentWebhookEvent, payload["id"]):
        return "", 204
    resource = payload["resource"]
    resource_id = resource.get("id")
    supplementary = resource.get("supplementary_data", {})
    related = supplementary.get("related_ids", {}) if isinstance(supplementary, dict) else None
    if not isinstance(related, dict) or not provider_identifier(resource_id):
        return jsonify(error="Invalid notification"), 400
    capture_id = related.get("capture_id") if event_name == "PAYMENT.CAPTURE.REFUNDED" else resource_id
    # Refund resources sometimes carry the capture ID only in their up link.
    if not capture_id and event_name == "PAYMENT.CAPTURE.REFUNDED":
        for link in resource.get("links", []):
            if link.get("rel") == "up" and isinstance(link.get("href"), str):
                parsed = urlsplit(link["href"])
                allowed = (
                    ("api.sandbox.paypal.com", "api-m.sandbox.paypal.com")
                    if current_app.config["PAYPAL_MODE"] == "sandbox"
                    else ("api.paypal.com", "api-m.paypal.com")
                )
                if parsed.scheme == "https" and parsed.netloc in allowed:
                    match = re.fullmatch(r"/v2/payments/captures/([A-Z0-9]{1,20})", parsed.path)
                    capture_id = match.group(1) if match else None
    order_id = related.get("order_id")
    if not provider_identifier(capture_id) or order_id and not provider_identifier(order_id):
        return jsonify(error="Invalid notification"), 400
    order = db.session.scalar(
        select(PaymentOrder).where(
            PaymentOrder.provider == "paypal",
            PaymentOrder.provider_mode == current_app.config["PAYPAL_MODE"],
            PaymentOrder.payment_reference == capture_id,
        )
    )
    if order is None and order_id:
        order = db.session.scalar(
            select(PaymentOrder).where(
                PaymentOrder.provider == "paypal",
                PaymentOrder.provider_mode == current_app.config["PAYPAL_MODE"],
                PaymentOrder.provider_id == order_id,
            )
        )
    if order is None:
        return "", 204
    event = {"id": payload["id"], "event": event_name, "provider_id": capture_id, "resource_id": resource_id}
    try:
        if event_name == "PAYMENT.CAPTURE.REVERSED" and (
            amount(resource["amount"]["value"]) != order.amount or resource["amount"]["currency_code"] != order.currency
        ):
            return jsonify(error="Invalid notification"), 400
        confirm_order(order, event)
    except (GatewayError, ConfirmationError, SQLAlchemyError, ValueError, KeyError, TypeError):
        db.session.rollback()
        current_app.logger.warning("PayPal notification awaits provider verification")
        return jsonify(error="Payment confirmation temporarily unavailable"), 503
    return "", 204


def register_payment_callbacks(app):
    app.add_url_rule(
        urlsplit(app.config["PAYMENT_RETURN_URL"]).path,
        endpoint="payments.return_page",
        view_func=return_page,
        methods=["GET"],
    )
    app.add_url_rule(
        urlsplit(app.config["PAYPAL_WEBHOOK_URL"]).path,
        endpoint="payments.webhook",
        view_func=webhook,
        methods=["POST"],
    )
