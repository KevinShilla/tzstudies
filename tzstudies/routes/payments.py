"""Private order UI, Hosted Checkout navigation and verified ClickPesa callbacks."""

import hashlib
import json
import re
from urllib.parse import urlsplit

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from tzstudies.clickpesa import GatewayError, valid_checkout_url, verify_checksum
from tzstudies.extensions import csrf, db, limiter
from tzstudies.payment_config import amount, plan_available
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent
from tzstudies.payments import ConfirmationError, confirm_order, create_order, new_intent, read_intent
from tzstudies.routes.admin import admin_required

payments_bp = Blueprint("payments", __name__)


def _owned_order(identifier):
    if not re.fullmatch(r"[a-f0-9]{32}", identifier):
        abort(404)
    order = db.session.get(PaymentOrder, identifier)
    if not order or order.user_id != current_user.id and not current_user.is_admin:
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
    available = {key: plan for key, plan in plans.items() if plan_available(plan, current_user)} if current_app.config["PAYMENTS_ENABLED"] else {}
    return render_template("payments/index.html", plans=available, intents={key: new_intent(key) for key in available}, orders=_orders())


@payments_bp.get("/admin/payments")
@admin_required
def admin():
    plans = current_app.extensions["payment_catalog"]["plans"]
    return render_template("payments/admin.html", plans=plans, intents={key: new_intent(key) for key in plans}, orders=_orders(admin=True),
                           enabled=current_app.config["PAYMENTS_ENABLED"],
                           credentials_ready=all(current_app.config.get(key) for key in ("CLICKPESA_CLIENT_ID", "CLICKPESA_API_KEY")),
                           return_url=current_app.config["PAYMENT_RETURN_URL"], webhook_url=current_app.config["CLICKPESA_WEBHOOK_URL"],
                           checksum_enabled=bool(current_app.config["CLICKPESA_CHECKSUM_KEY"]))


def _checkout_navigation(order):
    if order.status == "pending" and valid_checkout_url(order.checkout_url, current_app.config["CLICKPESA_CHECKOUT_DOMAINS"]):
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
            checkout_url = current_app.extensions["clickpesa"].create_checkout(order)
            if not valid_checkout_url(checkout_url, current_app.config["CLICKPESA_CHECKOUT_DOMAINS"]):
                raise GatewayError("invalid_response")
            # A fast webhook may have completed this order while checkout was being created.
            db.session.execute(update(PaymentOrder).where(PaymentOrder.id == order.id, PaymentOrder.status == "creating")
                               .values(checkout_url=checkout_url, status="pending"))
            db.session.commit()
        except GatewayError:
            db.session.rollback()
            # A timeout could mean a checkout was created. Never automatically create it again.
            db.session.execute(update(PaymentOrder).where(PaymentOrder.id == order.id, PaymentOrder.status == "creating")
                               .values(status="checkout_unknown"))
            db.session.commit()
            flash("Checkout could not be opened. Your order was saved. Check its status before trying another payment.", "warning")
        db.session.expire_all()
    return _checkout_navigation(order)


@payments_bp.get("/payments/orders/<identifier>")
@login_required
def order_page(identifier):
    return render_template("payments/order.html", order=_owned_order(identifier), returned=False)


@payments_bp.get("/payments/orders/<identifier>/continue")
@login_required
def continue_checkout(identifier):
    return _checkout_navigation(_owned_order(identifier))


@payments_bp.get("/payments/orders/<identifier>/status")
@login_required
def order_status(identifier):
    order = _owned_order(identifier)
    return jsonify(status=order.status, completed_at=order.completed_at.isoformat() + "Z" if order.completed_at else None)


@payments_bp.post("/payments/orders/<identifier>/check")
@login_required
@limiter.limit("6 per hour; 1 per minute")
def check_order(identifier):
    order = _owned_order(identifier)
    try:
        confirm_order(order)
        flash("Payment status checked with ClickPesa.", "success")
    except (GatewayError, ConfirmationError, SQLAlchemyError):
        db.session.rollback()
        flash("Payment has not been confirmed. Please wait, then check again. Do not make another payment yet.", "warning")
    return redirect(url_for("payments.order_page", identifier=order.id), code=303)


@login_required
def return_page():
    # Return query parameters are navigation hints only. Never accept status, amount or success.
    reference = request.args.get("orderReference")
    if reference:
        if not re.fullmatch(r"[a-zA-Z0-9]{1,40}", reference):
            abort(400)
        order = db.session.scalar(select(PaymentOrder).where(PaymentOrder.order_reference == reference))
        if not order:
            abort(404)
        order = _owned_order(order.id)
    else:
        identifier = session.get("payment_order")
        order = _owned_order(identifier) if isinstance(identifier, str) else None
    return render_template("payments/order.html", order=order, returned=True)


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
    if not request.is_json or request.content_length and request.content_length > 16384:
        return jsonify(error="Invalid notification"), 400
    try:
        body = request.get_data(cache=False)
        if len(body) > 16384:
            raise ValueError
        payload = json.loads(body, object_pairs_hook=_unique_object)
        if not isinstance(payload, dict) or payload.get("event") not in ("PAYMENT RECEIVED", "PAYMENT FAILED") or not isinstance(payload.get("data"), dict):
            raise ValueError
        data = payload["data"]
        reference, provider_id = data.get("orderReference"), data.get("id")
        if not isinstance(reference, str) or not re.fullmatch(r"[a-zA-Z0-9]{1,40}", reference) or not isinstance(provider_id, str) or not re.fullmatch(r"[a-zA-Z0-9._:-]{1,160}", provider_id):
            raise ValueError
    except (ValueError, TypeError, RecursionError):
        return jsonify(error="Invalid notification"), 400
    key = current_app.config["CLICKPESA_CHECKSUM_KEY"]
    if key and not verify_checksum(payload, key):
        return jsonify(error="Invalid notification signature"), 403
    order = db.session.scalar(select(PaymentOrder).where(PaymentOrder.order_reference == reference))
    if not order:
        return "", 204
    event = {"id": hashlib.sha256((payload["event"] + "|" + provider_id).encode()).hexdigest(), "event": payload["event"], "provider_id": provider_id}
    if db.session.get(PaymentWebhookEvent, event["id"]):
        return "", 204
    if not all(current_app.config.get(name) for name in ("CLICKPESA_CLIENT_ID", "CLICKPESA_API_KEY")):
        return jsonify(error="Payment confirmation temporarily unavailable"), 503
    if data.get("clientId", current_app.config["CLICKPESA_CLIENT_ID"]) != current_app.config["CLICKPESA_CLIENT_ID"]:
        return jsonify(error="Invalid notification"), 400
    if payload["event"] == "PAYMENT RECEIVED":
        try:
            if amount(data.get("collectedAmount")) != order.amount or data.get("collectedCurrency") != order.currency:
                raise ValueError
        except ValueError:
            return jsonify(error="Invalid notification amount"), 400
    try:
        confirm_order(order, event)
    except (GatewayError, ConfirmationError, SQLAlchemyError):
        db.session.rollback()
        # No receipt is stored on failure, so retries/reconciliation can still verify it later.
        current_app.logger.warning("ClickPesa notification awaits provider verification")
        return jsonify(error="Payment confirmation temporarily unavailable"), 503
    return "", 204


def register_payment_callbacks(app):
    app.add_url_rule(urlsplit(app.config["PAYMENT_RETURN_URL"]).path, endpoint="payments.return_page", view_func=return_page, methods=["GET"])
    app.add_url_rule(urlsplit(app.config["CLICKPESA_WEBHOOK_URL"]).path, endpoint="payments.webhook", view_func=webhook, methods=["POST"])
