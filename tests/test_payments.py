"""PayPal contract, payment ownership, CSRF and financially safe replay behavior."""

import copy
import re
from contextlib import contextmanager
from datetime import timedelta
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import select, text

from tzstudies.payment_config import configure_payments, money_text
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent, upgrade_payment_schema, utcnow
from tzstudies.payments import ConfirmationError, verified_record
from tzstudies.paypal import GatewayError, PayPal, binding, request_id, valid_checkout_url

WEBHOOK = "/payments/webhooks/paypal"


class MockGateway:
    base = "https://api-m.sandbox.paypal.com"

    def __init__(self):
        self.created = []
        self.captures = []
        self.records = {}
        self.capture_status = "COMPLETED"
        self.error = False
        self.valid_signature = True
        self.refund = None

    def create_checkout(self, order):
        self.created.append(order.id)
        if self.error:
            raise GatewayError()
        data = {
            "id": "ORDER123456789",
            "intent": "CAPTURE",
            "status": "PAYER_ACTION_REQUIRED",
            "purchase_units": [
                {
                    "reference_id": order.id,
                    "custom_id": binding(order),
                    "invoice_id": order.order_reference,
                    "amount": {"value": str(order.amount), "currency_code": order.currency},
                    "items": [
                        {
                            "name": order.plan_name,
                            "sku": order.plan_id,
                            "quantity": "1",
                            "category": "DIGITAL_GOODS",
                            "unit_amount": {"value": str(order.amount), "currency_code": order.currency},
                        }
                    ],
                }
            ],
            "links": [
                {
                    "rel": "payer-action",
                    "method": "GET",
                    "href": "https://www.sandbox.paypal.com/checkoutnow?token=ORDER123456789",
                }
            ],
        }
        self.records[data["id"]] = data
        return copy.deepcopy(data)

    def get_order(self, identifier):
        if self.error:
            raise GatewayError()
        return copy.deepcopy(self.records[identifier])

    def approve(self):
        self.records["ORDER123456789"]["status"] = "APPROVED"

    def capture_order(self, order):
        self.captures.append(order.id)
        if self.error:
            raise GatewayError()
        data = self.records[order.provider_id]
        data["status"] = "COMPLETED"
        unit = data["purchase_units"][0]
        unit["payments"] = {
            "captures": [
                {
                    "id": "CAPTURE1234567",
                    "status": self.capture_status,
                    "final_capture": True,
                    "amount": unit["amount"],
                    "invoice_id": order.order_reference,
                    "custom_id": binding(order),
                    "supplementary_data": {"related_ids": {"order_id": order.provider_id}},
                }
            ]
        }
        return copy.deepcopy(data)

    def get_capture(self, identifier):
        if self.error:
            raise GatewayError()
        return copy.deepcopy(self.records["ORDER123456789"]["purchase_units"][0]["payments"]["captures"][0])

    def get_refund(self, identifier):
        return copy.deepcopy(self.refund)

    def verify_webhook(self, payload, headers, raw_body=None):
        return self.valid_signature


@pytest.fixture
def payment_setup(app, monkeypatch):
    for key, value in {
        "PAYMENTS_ENABLED": True,
        "PAYMENT_TEST_PLAN_ENABLED": True,
        "PAYPAL_CLIENT_ID": "mock-client",
        "PAYPAL_CLIENT_SECRET": "mock-secret",
        "PAYPAL_WEBHOOK_ID": "mock-webhook",
        "PAYPAL_MODE": "sandbox",
    }.items():
        monkeypatch.setitem(app.config, key, value)
    catalog = copy.deepcopy(app.extensions["payment_catalog"])
    catalog["plans"]["payment_test"]["enabled"] = True
    monkeypatch.setitem(app.extensions, "payment_catalog", catalog)
    gateway = MockGateway()
    monkeypatch.setitem(app.extensions, "paypal", gateway)
    return gateway


@pytest.fixture
def payment_admin(app, auth_client, sample_user, db):
    with app.app_context():
        db.session.query(type(sample_user)).filter_by(email="test@example.com").one().is_admin = True
        db.session.commit()
    return auth_client


def start(client):
    page = client.get("/admin/payments")
    assert page.status_code == 200
    token = re.search(rb'name="intent" value="([^"]+)"', page.data).group(1).decode()
    response = client.post(
        "/payments/checkout/payment_test", data={"intent": token, "amount": "999", "currency": "TZS", "user_id": "999"}
    )
    return token, response


def local_order(app, db):
    with app.app_context():
        return db.session.scalar(select(PaymentOrder))


def capture(client, order):
    return client.post(f"/payments/orders/{order.id}/capture", data={"token": order.provider_id})


def notification(gateway, event="PAYMENT.CAPTURE.COMPLETED", event_id="WH-MOCK1"):
    resource = gateway.get_capture("CAPTURE1234567")
    if event == "PAYMENT.CAPTURE.REFUNDED":
        resource = copy.deepcopy(gateway.refund)
        resource["supplementary_data"] = {"related_ids": {"capture_id": "CAPTURE1234567", "order_id": "ORDER123456789"}}
    return {"id": event_id, "event_type": event, "resource": resource}


def test_paused_and_admin_permissions(app, client, auth_client):
    assert app.test_client().get("/admin/payments").status_code == 302
    assert auth_client.get("/admin/payments").status_code == 403
    assert auth_client.post("/payments/checkout/payment_test").status_code == 404
    assert client.post(WEBHOOK, json={}).status_code == 503
    assert client.post("/payments/webhooks/clickpesa", json={}).status_code == 404


def test_server_price_and_duplicate_intent(app, db, payment_setup, payment_admin):
    token, response = start(payment_admin)
    assert response.status_code == 200
    assert b"window.location.replace" in response.data
    assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store, private"
    order = local_order(app, db)
    assert order.amount == Decimal("1.00") and order.currency == "USD" and order.provider == "paypal"
    assert order.provider_mode == "sandbox" and order.plan_snapshot["features"] == []
    assert payment_admin.post("/payments/checkout/payment_test", data={"intent": token}).status_code == 200
    assert len(payment_setup.created) == 1


def test_return_alone_never_confirms(app, db, payment_setup, payment_admin):
    start(payment_admin)
    order = local_order(app, db)
    response = payment_admin.get(f"/payments/return?order={order.id}&token={order.provider_id}&status=COMPLETED")
    assert response.status_code == 200 and b"captureApproved" in response.data
    assert local_order(app, db).status == "pending" and payment_setup.captures == []
    assert payment_admin.get(f"/payments/return?order={order.id}&token=WRONG123").status_code == 400
    assert capture(payment_admin, order).status_code == 303
    assert local_order(app, db).status == "pending"  # provider has not approved


@pytest.mark.parametrize(
    "status,expected", [("COMPLETED", "paid"), ("PENDING", "processing"), ("DECLINED", "failed"), ("FAILED", "failed")]
)
def test_capture_states(app, db, payment_setup, payment_admin, status, expected):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    payment_setup.capture_status = status
    assert capture(payment_admin, order).status_code == 303
    stored = local_order(app, db)
    assert stored.status == expected
    assert bool(stored.completed_at) == (status == "COMPLETED")
    assert stored.payment_reference == "CAPTURE1234567"
    assert payment_admin.get(f"/payments/orders/{order.id}").status_code == 200


def test_capture_replay_and_signature_webhook_replay(app, db, payment_setup, payment_admin):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    capture(payment_admin, order)
    completed = local_order(app, db).completed_at
    capture(payment_admin, order)
    assert len(payment_setup.captures) == 1
    payload = notification(payment_setup)
    assert payment_admin.post(WEBHOOK, json=payload).status_code == 204
    assert payment_admin.post(WEBHOOK, json=payload).status_code == 204
    with app.app_context():
        assert db.session.query(PaymentWebhookEvent).count() == 1
        assert db.session.get(PaymentOrder, order.id).completed_at == completed
    payment_setup.valid_signature = False
    assert payment_admin.post(WEBHOOK, json=payload).status_code == 403


def test_webhook_recovers_capture_when_browser_closed(app, db, payment_setup, payment_admin):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    payment_setup.capture_order(order)
    assert payment_admin.post(WEBHOOK, json=notification(payment_setup)).status_code == 204
    assert local_order(app, db).status == "paid"


@pytest.mark.parametrize(
    "field",
    [
        "order_id",
        "amount",
        "currency",
        "custom_id",
        "invoice_id",
        "sku",
        "name",
        "user",
        "multiple_captures",
        "capture_id",
        "final_capture",
    ],
)
def test_mismatched_financial_data_rejected(app, db, payment_setup, payment_admin, field):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    payment_setup.capture_order(order)
    data = payment_setup.records[order.provider_id]
    unit = data["purchase_units"][0]
    if field == "order_id":
        data["id"] = "WRONG123"
    elif field == "amount":
        unit["amount"]["value"] = "2.00"
    elif field == "currency":
        unit["amount"]["currency_code"] = "EUR"
    elif field == "custom_id":
        unit["custom_id"] = "wrong"
    elif field == "invoice_id":
        unit["invoice_id"] = "wrong"
    elif field == "sku":
        unit["items"][0]["sku"] = "wrong"
    elif field == "name":
        unit["items"][0]["name"] = "wrong"
    elif field == "user":
        with app.app_context():
            db.session.get(PaymentOrder, order.id).user_id += 999
            # Verify detached expected-user mutation without a foreign-key DB update.
            db.session.rollback()
        order.user_id += 999
    elif field == "multiple_captures":
        unit["payments"]["captures"].append(copy.deepcopy(unit["payments"]["captures"][0]))
    elif field == "capture_id":
        unit["payments"]["captures"][0]["id"] = "bad!"
    elif field == "final_capture":
        unit["payments"]["captures"][0]["final_capture"] = False
    with app.app_context(), pytest.raises(ConfirmationError):
        verified_record(order, data)
    assert local_order(app, db).completed_at is None


def test_cancellation_and_other_users_order(app, db, payment_setup, payment_admin):
    start(payment_admin)
    order = local_order(app, db)
    assert payment_admin.get(f"/payments/return?order={order.id}&cancelled=1").status_code == 200
    assert local_order(app, db).status == "pending"
    assert payment_admin.post(f"/payments/orders/{order.id}/cancel").status_code == 303
    payment_setup.approve()
    capture(payment_admin, order)
    assert local_order(app, db).status == "cancelled" and payment_setup.captures == []
    from tzstudies.models import User

    with app.app_context():
        from tzstudies.security import hash_password

        user = User(
            name="Other",
            email="other@example.test",
            pw_hash=hash_password("Another river remembers sunrise!"),
            is_admin=True,
        )
        db.session.add(user)
        db.session.commit()
        other_id = user.id
    other = app.test_client()
    other.post("/login", data={"email": "other@example.test", "password": "Another river remembers sunrise!"})
    assert other.get(f"/payments/orders/{order.id}").status_code == 200  # admin read-only
    assert other.post(f"/payments/orders/{order.id}/capture", data={"token": order.provider_id}).status_code == 404
    assert other.get(f"/payments/return?order={order.id}&token={order.provider_id}").status_code == 404
    with app.app_context():
        db.session.get(User, other_id).is_admin = False
        db.session.commit()
    assert other.get(f"/payments/orders/{order.id}").status_code == 404


@pytest.mark.parametrize(
    "status,event",
    [
        ("REFUNDED", "PAYMENT.CAPTURE.REFUNDED"),
        ("PARTIALLY_REFUNDED", "PAYMENT.CAPTURE.REFUNDED"),
        ("COMPLETED", "PAYMENT.CAPTURE.REVERSED"),
    ],
)
def test_refunds_reversals_cannot_be_resurrected(app, db, payment_setup, payment_admin, status, event):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    capture(payment_admin, order)
    payment_setup.records[order.provider_id]["purchase_units"][0]["payments"]["captures"][0]["status"] = status
    payment_setup.refund = {
        "id": "REFUND123456",
        "status": "COMPLETED",
        "amount": {"value": "1.00" if status == "REFUNDED" else "0.50", "currency_code": "USD"},
    }
    assert payment_admin.post(WEBHOOK, json=notification(payment_setup, event)).status_code == 204
    before = local_order(app, db).status
    assert before == ("reversed" if event.endswith("REVERSED") else status.lower())
    assert local_order(app, db).refunded_at
    payment_setup.records[order.provider_id]["purchase_units"][0]["payments"]["captures"][0]["status"] = "COMPLETED"
    assert payment_admin.post(WEBHOOK, json=notification(payment_setup, event_id="WH-REPLAY2")).status_code == 204
    assert local_order(app, db).status == before


def test_webhook_invalid_body_and_unconfirmed_capture(app, db, payment_setup, payment_admin):
    assert payment_admin.post(WEBHOOK, data='{"id":"a","id":"b"}', content_type="application/json").status_code == 400
    assert payment_admin.post(WEBHOOK, json={}).status_code == 400
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    payment_setup.capture_status = "PENDING"
    payment_setup.capture_order(order)
    assert payment_admin.post(WEBHOOK, json=notification(payment_setup)).status_code == 503
    assert local_order(app, db).completed_at is None


def test_pending_to_completed_webhook(app, db, payment_setup, payment_admin):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    payment_setup.capture_status = "PENDING"
    capture(payment_admin, order)
    assert payment_admin.post(WEBHOOK, json=notification(payment_setup, "PAYMENT.CAPTURE.PENDING")).status_code == 204
    payment_setup.records[order.provider_id]["purchase_units"][0]["payments"]["captures"][0]["status"] = "COMPLETED"
    assert payment_admin.post(WEBHOOK, json=notification(payment_setup, event_id="WH-COMPLETED2")).status_code == 204
    assert local_order(app, db).status == "paid"


def test_creation_error_does_not_repeat(app, db, payment_setup, payment_admin):
    payment_setup.error = True
    token, response = start(payment_admin)
    assert response.status_code == 303
    assert local_order(app, db).status == "checkout_unknown"
    payment_admin.post("/payments/checkout/payment_test", data={"intent": token})
    assert len(payment_setup.created) == 1


def test_minimal_create_and_capture_responses(app, db, payment_setup, payment_admin, monkeypatch):
    create = payment_setup.create_checkout

    def minimal_create(order):
        full = create(order)
        return {k: full[k] for k in ("id", "status", "links")}

    monkeypatch.setattr(payment_setup, "create_checkout", minimal_create)
    start(payment_admin)
    order = local_order(app, db)
    assert order.status == "pending"
    original = payment_setup.capture_order

    def minimal_capture(order):
        full = original(order)
        return {k: full[k] for k in ("id", "status")}

    monkeypatch.setattr(payment_setup, "capture_order", minimal_capture)
    payment_setup.approve()
    capture(payment_admin, order)
    assert local_order(app, db).status == "paid"


def test_capture_unknown_saved_and_safe_retry(app, db, payment_setup, payment_admin, monkeypatch):
    start(payment_admin)
    order = local_order(app, db)
    payment_setup.approve()
    original = payment_setup.capture_order

    def timeout(order):
        raise GatewayError()

    monkeypatch.setattr(payment_setup, "capture_order", timeout)
    capture(payment_admin, order)
    assert local_order(app, db).status == "processing" and local_order(app, db).capture_requested_at
    with app.app_context():
        db.session.get(PaymentOrder, order.id).capture_requested_at = utcnow() - timedelta(hours=7)
        db.session.commit()
    monkeypatch.setattr(payment_setup, "capture_order", original)
    capture(payment_admin, order)
    assert payment_setup.captures == []


def test_csrf_on_every_browser_mutation(app, db, payment_setup, payment_admin, monkeypatch):
    start(payment_admin)
    order = local_order(app, db)
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)
    for path in (
        "/payments/checkout/payment_test",
        f"/payments/orders/{order.id}/capture",
        f"/payments/orders/{order.id}/cancel",
        f"/payments/orders/{order.id}/check",
    ):
        assert payment_admin.post(path).status_code == 400
    page = payment_admin.get("/admin/payments")
    csrf = re.search(rb'name="csrf_token" value="([^"]+)"', page.data).group(1).decode()
    assert payment_admin.post(f"/payments/orders/{order.id}/cancel", data={"csrf_token": csrf}).status_code == 303


def test_no_secrets_in_pages(app, db, payment_setup, payment_admin):
    _, response = start(payment_admin)
    order = local_order(app, db)
    for page in (response, payment_admin.get("/admin/payments"), payment_admin.get(f"/payments/orders/{order.id}")):
        assert b"mock-secret" not in page.data and b"mock-client" not in page.data and b"mock-webhook" not in page.data


def test_legacy_order_cannot_be_captured(app, db, payment_setup, payment_admin):
    start(payment_admin)
    order = local_order(app, db)
    with app.app_context():
        db.session.get(PaymentOrder, order.id).provider = "clickpesa"
        db.session.commit()
    capture(payment_admin, order)
    assert payment_setup.captures == []
    assert b"Archived order" in payment_admin.get(f"/payments/orders/{order.id}").data


def test_config_sandbox_currency_safety(app, monkeypatch):
    config = copy.deepcopy(app.config)
    catalog = copy.deepcopy(app.extensions["payment_catalog"])
    import tzstudies.payment_config as module

    monkeypatch.setattr(module, "load_catalog", lambda path: copy.deepcopy(catalog))
    monkeypatch.setitem(app.config, "PAYMENT_TEST_PLAN_ENABLED", True)
    monkeypatch.setitem(app.config, "PAYPAL_MODE", "live")
    with pytest.raises(RuntimeError):
        configure_payments(app)
    monkeypatch.setitem(app.config, "PAYPAL_MODE", "sandbox")
    monkeypatch.setitem(app.config, "PAYMENT_TEST_PLAN_ENABLED", False)
    catalog["plans"]["payment_test"].update(enabled=True, admin_only=False)
    with pytest.raises(RuntimeError):
        configure_payments(app)
    app.config.update(config)


@pytest.mark.parametrize(
    "url,mode,expected",
    [
        ("https://www.sandbox.paypal.com/checkoutnow?token=ABC", "sandbox", True),
        ("https://www.paypal.com/checkoutnow?token=ABC", "sandbox", False),
        ("https://www.sandbox.paypal.com.evil.test/checkoutnow", "sandbox", False),
        ("https://www.paypal.com/checkoutnow", "live", True),
        ("https://evil.test/checkoutnow", "live", False),
        ("http://www.sandbox.paypal.com/checkoutnow", "sandbox", False),
    ],
)
def test_checkout_hosts(url, mode, expected):
    assert valid_checkout_url(url, mode) == expected


def test_money_precision():
    assert money_text("1.00", "USD") == "1.00"
    assert money_text("100", "JPY") == "100"
    for value, currency in (("1.50", "JPY"), ("1000", "TZS"), ("NaN", "USD"), (True, "USD")):
        with pytest.raises(ValueError):
            money_text(value, currency)


def test_provider_requests_oauth_idempotency_and_signature(app, db, payment_setup, payment_admin, monkeypatch):
    start(payment_admin)
    order = local_order(app, db)
    client = PayPal(app.config)
    calls = []

    @contextmanager
    def stream(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if url.endswith("/token"):
            body = {"access_token": "mock-oauth-token", "token_type": "Bearer", "expires_in": 3600}
        elif url.endswith("/verify-webhook-signature"):
            body = {"verification_status": "SUCCESS"}
        elif url.endswith("/capture"):
            body = payment_setup.capture_order(order)
        else:
            body = payment_setup.get_order(order.provider_id)
        yield httpx.Response(201 if url.endswith("/orders") else 200, json=body)

    monkeypatch.setattr(httpx, "stream", stream)
    client.create_checkout(order)
    client.capture_order(order)
    headers = {
        "PAYPAL-AUTH-ALGO": "SHA256withRSA",
        "PAYPAL-CERT-URL": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT1",
        "PAYPAL-TRANSMISSION-ID": "ID1",
        "PAYPAL-TRANSMISSION-SIG": "signature",
        "PAYPAL-TRANSMISSION-TIME": "2026-10-12T12:00:00Z",
    }
    assert client.verify_webhook({"id": "WH-1"}, headers)
    bad = dict(headers, **{"PAYPAL-CERT-URL": "https://evil.test/cert"})
    assert not client.verify_webhook({}, bad)
    assert not client.verify_webhook({}, {})
    assert all(url.startswith("https://api-m.sandbox.paypal.com/") for _, url, _ in calls)
    posts = [kwargs for _, url, kwargs in calls if url.endswith("/orders") or url.endswith("/capture")]
    assert posts[0]["headers"]["PayPal-Request-Id"] == request_id(order, "create")
    assert posts[1]["headers"]["PayPal-Request-Id"] == request_id(order, "capture")
    assert posts[0]["headers"]["PayPal-Request-Id"] != posts[1]["headers"]["PayPal-Request-Id"]
    assert posts[0]["json"]["payment_source"]["paypal"]["experience_context"]["user_action"] == "PAY_NOW"
    assert all(kwargs["follow_redirects"] is False and kwargs["trust_env"] is False for _, _, kwargs in calls)


def test_provider_failure_never_exposes_body(app, monkeypatch):
    client = PayPal(app.config)

    @contextmanager
    def stream(*args, **kwargs):
        yield httpx.Response(422, json={"private": "DO-NOT-EXPOSE"})

    monkeypatch.setattr(httpx, "stream", stream)
    with pytest.raises(GatewayError) as error:
        client._request("POST", "/v2/checkout/orders", {})
    assert "DO-NOT-EXPOSE" not in str(error.value)


def test_upgrade_old_schema_preserves_records():
    from sqlalchemy import create_engine, inspect

    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE payment_order (id VARCHAR(32) PRIMARY KEY, status VARCHAR(24))"))
        conn.execute(text("INSERT INTO payment_order VALUES ('legacy','pending')"))
        upgrade_payment_schema(conn)
        upgrade_payment_schema(conn)
        assert conn.execute(text("SELECT provider, status FROM payment_order")).one() == ("clickpesa", "pending")
        assert "refunded_at" in {c["name"] for c in inspect(conn).get_columns("payment_order")}
    engine.dispose()
