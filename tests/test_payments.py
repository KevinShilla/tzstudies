"""Payment trust boundaries, provider contract, access control and replay safety."""
import copy
import json
import re
from contextlib import contextmanager
from decimal import Decimal
from unittest.mock import Mock
from urllib.parse import urlsplit

import httpx
import pytest
from sqlalchemy import select

from tzstudies.clickpesa import ClickPesa, GatewayError, checksum, valid_checkout_url, verify_checksum
from tzstudies.payment_config import amount, configure_payments
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent
from tzstudies.payments import ConfirmationError, apply_confirmation

WEBHOOK = "/payments/webhooks/clickpesa"


class MockGateway:
    def __init__(self):
        self.created = []
        self.queries = []
        self.records = []
        self.error = None

    def create_checkout(self, order):
        self.created.append(order.order_reference)
        if self.error:
            raise GatewayError()
        return "https://checkout.clickpesa.com/mock/" + order.order_reference

    def query_payment(self, reference):
        self.queries.append(reference)
        if self.error:
            raise GatewayError()
        return copy.deepcopy(self.records)


@pytest.fixture
def payment_setup(app, monkeypatch):
    monkeypatch.setitem(app.config, "PAYMENTS_ENABLED", True)
    monkeypatch.setitem(app.config, "CLICKPESA_CLIENT_ID", "mock-client")
    monkeypatch.setitem(app.config, "CLICKPESA_API_KEY", "mock-api-key")
    monkeypatch.setitem(app.config, "CLICKPESA_CHECKSUM_KEY", "")
    catalog = copy.deepcopy(app.extensions["payment_catalog"])
    catalog["plans"]["payment_test"]["enabled"] = True
    monkeypatch.setitem(app.extensions, "payment_catalog", catalog)
    gateway = MockGateway()
    monkeypatch.setitem(app.extensions, "clickpesa", gateway)
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
    response = client.post("/payments/checkout/payment_test", data={"intent": token, "amount": "1", "currency": "USD", "price": "1"})
    return token, response


def order_data(app, db):
    with app.app_context():
        order = db.session.scalar(select(PaymentOrder))
        return order.id, order.order_reference


def provider_record(reference, **changes):
    record = {"id": "provider-transaction-1", "clientId": "mock-client", "orderReference": reference,
              "status": "SUCCESS", "collectedAmount": 1000, "collectedCurrency": "TZS", "paymentReference": "receipt-1"}
    record.update(changes)
    return record


def notification(record, event="PAYMENT RECEIVED"):
    return {"event": event, "data": copy.deepcopy(record)}


def test_admin_only_and_disabled_by_default(app, client, auth_client, db, sample_user):
    assert app.test_client().get("/admin/payments").status_code == 302
    assert auth_client.get("/admin/payments").status_code == 403
    assert auth_client.post("/payments/checkout/payment_test", data={}).status_code == 404
    assert b"payment_test" not in auth_client.get("/payments").data
    assert auth_client.get("/").status_code == 200
    with app.app_context():
        assert db.session.query(type(sample_user)).filter_by(is_admin=True).count() == 0


def test_checkout_uses_snapshot_and_reuses_intent(app, db, payment_setup, payment_admin):
    token, response = start(payment_admin)
    assert response.status_code == 200 and b"window.location.replace" in response.data
    assert "form-action 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store, private"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    with app.app_context():
        order = db.session.scalar(select(PaymentOrder))
        assert order.amount == Decimal("1000.00") and order.currency == "TZS"
        assert re.fullmatch(r"[A-Z0-9]{34}", order.order_reference)
        assert order.plan_snapshot["ai_allowance"] == 0
    assert payment_admin.post("/payments/checkout/payment_test", data={"intent": token}).status_code == 200
    assert len(payment_setup.created) == 1


def test_user_cannot_purchase_admin_test(app, payment_setup, auth_client):
    assert auth_client.post("/payments/checkout/payment_test", data={"intent": "forged"}).status_code == 404
    assert not payment_setup.created


def test_invalid_intent_and_unknown_plan(payment_setup, payment_admin):
    assert payment_admin.post("/payments/checkout/payment_test", data={"intent": "forged"}).status_code == 400
    assert payment_admin.post("/payments/checkout/unknown", data={}).status_code == 404
    assert not payment_setup.created


def test_return_never_confirms_and_is_private(app, db, payment_setup, payment_admin, client):
    start(payment_admin)
    identifier, reference = order_data(app, db)
    response = payment_admin.get("/payments/return?success=true&status=SUCCESS&amount=1000&orderReference=" + reference)
    assert response.status_code == 200 and b"Awaiting payment confirmation" in response.data
    assert not payment_setup.queries
    assert payment_admin.get(f"/payments/orders/{identifier}/status").json["status"] == "pending"
    assert app.test_client().get(f"/payments/orders/{identifier}/status").status_code == 302
    assert payment_admin.get("/payments/return?orderReference=bad%2Freference").status_code == 400


def test_other_user_cannot_see_order(app, db, payment_setup, payment_admin, sample_user):
    from tzstudies.models import User
    from tzstudies.security import hash_password
    start(payment_admin)
    identifier, reference = order_data(app, db)
    with app.app_context():
        db.session.add(User(name="Other", email="other@example.test", pw_hash=hash_password("Sunsets paint mountains!")))
        db.session.commit()
    other = app.test_client()
    other.post("/login", data={"email": "other@example.test", "password": "Sunsets paint mountains!"})
    assert other.get(f"/payments/orders/{identifier}").status_code == 404
    assert other.get(f"/payments/orders/{identifier}/status").status_code == 404
    assert other.post(f"/payments/orders/{identifier}/check").status_code == 404
    assert other.get("/payments/return?orderReference=" + reference).status_code == 404


def test_valid_webhook_idempotence_no_sensitive_payload(app, db, payment_setup, payment_admin, client):
    start(payment_admin)
    identifier, reference = order_data(app, db)
    record = provider_record(reference)
    record["customer"] = {"customerName": "Private person", "customerEmail": "private@example.test", "customerPhoneNumber": "255700000000"}
    payment_setup.records = [record]
    payload = notification(record)
    assert client.post(WEBHOOK, json=payload).status_code == 204
    with app.app_context():
        db.session.expire_all()
        order = db.session.get(PaymentOrder, identifier)
        completed = order.completed_at
        assert order.status == "paid" and completed and order.checkout_url is None
        assert order.provider_id == record["id"] and order.payment_reference == record["paymentReference"]
        assert db.session.query(PaymentWebhookEvent).count() == 1
        assert "customer" not in order.plan_snapshot
        assert "customer" not in PaymentWebhookEvent.__table__.columns
    # Different JSON formatting/extra fields must not defeat replay protection.
    payload["extra"] = "replay"
    assert client.post(WEBHOOK, data=json.dumps(payload), content_type="application/json").status_code == 204
    assert len(payment_setup.queries) == 1
    with app.app_context():
        db.session.expire_all()
        assert db.session.get(PaymentOrder, identifier).completed_at == completed
        assert db.session.query(PaymentWebhookEvent).count() == 1
    assert payment_admin.get(f"/payments/orders/{identifier}/status").json["status"] == "paid"
    assert b"Payment confirmed" in payment_admin.get("/payments/return").data


@pytest.mark.parametrize("changes", [
    {"status": "PENDING"}, {"collectedAmount": 1}, {"collectedCurrency": "USD"},
    {"clientId": "wrong-client"}, {"id": "other-transaction"}, {"orderReference": "OTHERORDER"},
    {"paymentReference": "bad/ref"}, {"collectedAmount": "NaN"}, {"status": "UNKNOWN"},
])
def test_forged_success_cannot_complete(app, db, payment_setup, payment_admin, client, changes):
    start(payment_admin)
    identifier, reference = order_data(app, db)
    valid = provider_record(reference)
    payment_setup.records = [provider_record(reference, **changes)]
    assert client.post(WEBHOOK, json=notification(valid)).status_code == 503
    with app.app_context():
        db.session.expire_all()
        assert db.session.get(PaymentOrder, identifier).status == "pending"
        assert db.session.query(PaymentWebhookEvent).count() == 0


def test_notification_tampering_rejected_before_query(app, db, payment_setup, payment_admin, client):
    start(payment_admin)
    _, reference = order_data(app, db)
    payment_setup.records = [provider_record(reference)]
    assert client.post(WEBHOOK, json=notification(provider_record(reference, collectedAmount="1"))).status_code == 400
    assert not payment_setup.queries
    assert client.post(WEBHOOK, data='{"event":"PAYMENT RECEIVED","event":"PAYMENT FAILED"}', content_type="application/json").status_code == 400
    assert client.post(WEBHOOK, json={"event": "PAYOUT INITIATED", "data": {}}).status_code == 400
    assert client.post(WEBHOOK, data="not json").status_code == 400


def test_required_signature_missing_tampered_valid(app, db, payment_setup, payment_admin, client, monkeypatch):
    start(payment_admin)
    _, reference = order_data(app, db)
    payment_setup.records = [provider_record(reference)]
    monkeypatch.setitem(app.config, "CLICKPESA_CHECKSUM_KEY", "mock-checksum-secret")
    payload = notification(provider_record(reference))
    assert client.post(WEBHOOK, json=payload).status_code == 403
    payload["checksum"] = checksum(payload, "mock-checksum-secret")
    bad = copy.deepcopy(payload)
    bad["data"]["collectedAmount"] = 1
    assert client.post(WEBHOOK, json=bad).status_code == 403
    assert not payment_setup.queries
    assert client.post(WEBHOOK, json=payload).status_code == 204


def test_failure_without_amount_and_late_failure_preserves_success(app, db, payment_setup, payment_admin, client):
    start(payment_admin)
    identifier, reference = order_data(app, db)
    failed = {"id": "failed-attempt", "orderReference": reference, "clientId": "mock-client", "status": "FAILED"}
    payment_setup.records = [failed]
    assert client.post(WEBHOOK, json=notification(failed, "PAYMENT FAILED")).status_code == 204
    assert payment_admin.get(f"/payments/orders/{identifier}/status").json["status"] == "failed"
    paid = provider_record(reference)
    payment_setup.records = [paid]
    assert client.post(WEBHOOK, json=notification(paid)).status_code == 204
    late = dict(failed, id="late-failed-attempt")
    payment_setup.records = [late]
    assert client.post(WEBHOOK, json=notification(late, "PAYMENT FAILED")).status_code == 204
    assert payment_admin.get(f"/payments/orders/{identifier}/status").json["status"] == "paid"


def test_reconciliation_snapshot_and_terminal_refund(app, db, payment_setup, payment_admin):
    start(payment_admin)
    identifier, reference = order_data(app, db)
    app.extensions["payment_catalog"]["plans"]["payment_test"]["price"] = "5000.00"
    payment_setup.records = [provider_record(reference)]
    assert payment_admin.post(f"/payments/orders/{identifier}/check").status_code == 303
    with app.app_context():
        apply_confirmation(identifier, provider_record(reference, status="REFUNDED"))
        apply_confirmation(identifier, provider_record(reference))
        db.session.expire_all()
        order = db.session.get(PaymentOrder, identifier)
        assert order.amount == 1000 and order.status == "refunded" and order.provider_status == "REFUNDED"


def test_checkout_timeout_not_retried_or_marked_paid(app, db, payment_setup, payment_admin):
    payment_setup.error = True
    token, response = start(payment_admin)
    assert response.status_code == 303
    assert payment_admin.post("/payments/checkout/payment_test", data={"intent": token}).status_code == 303
    assert len(payment_setup.created) == 1
    with app.app_context():
        assert db.session.scalar(select(PaymentOrder)).status == "checkout_unknown"


def test_csrf_required_checkout_but_not_webhook(app, db, payment_setup, payment_admin, client, monkeypatch):
    token, _ = start(payment_admin)
    _, reference = order_data(app, db)
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)
    assert payment_admin.post("/payments/checkout/payment_test", data={"intent": token}).status_code == 400
    payment_setup.records = [provider_record(reference)]
    assert client.post(WEBHOOK, json=notification(provider_record(reference))).status_code == 204


@pytest.mark.parametrize("value", [float("nan"), "NaN", "1e3", "1000.001", True, "-1", "1,000", None])
def test_invalid_money(value):
    with pytest.raises(ValueError):
        amount(value)


@pytest.mark.parametrize("url", ["http://checkout.clickpesa.com/abc", "https://evilclickpesa.com/abc", "https://clickpesa.com.evil.test/abc", "https://clickpesa.com@evil.test/abc", "https://clickpesa.com:444/abc", "javascript:alert(1)", "https://clickpesa.com/abc\n"])
def test_unsafe_checkout_urls(url):
    assert not valid_checkout_url(url, ("clickpesa.com",))


def test_gateway_exact_api_contract_cached_token(app, payment_setup, monkeypatch):
    gateway = ClickPesa(app.config)
    calls = []
    def request(method, path, headers, payload=None):
        calls.append((method, path, headers, payload))
        if path == "/generate-token":
            return {"success": True, "token": "Bearer mock-token"}
        if method == "GET":
            return []
        return {"clientId": "mock-client", "checkoutLink": "https://checkout.clickpesa.com/mock"}
    monkeypatch.setattr(gateway, "_request", request)
    order = Mock(amount=Decimal("1000.00"), order_reference="TZABC123", currency="TZS", plan_name="Test")
    gateway.create_checkout(order)
    gateway.query_payment(order.order_reference)
    assert [call[1] for call in calls] == ["/generate-token", "/checkout-link/generate-checkout-url", "/payments/TZABC123"]
    assert calls[0][2]["client-id"] == "mock-client" and calls[0][2]["api-key"] == "mock-api-key"
    assert calls[1][2]["Authorization"] == "Bearer mock-token"
    assert calls[1][3] == {"totalPrice": "1000.00", "orderReference": "TZABC123", "orderCurrency": "TZS", "description": "Test"}


def test_gateway_http_errors_safe_no_redirect_or_retry(app, payment_setup, monkeypatch):
    calls = []
    @contextmanager
    def stream(method, url, **kwargs):
        calls.append(kwargs)
        yield httpx.Response(403, text="private provider body and mock-api-key")
    monkeypatch.setattr(httpx, "stream", stream)
    with pytest.raises(GatewayError) as error:
        ClickPesa(app.config)._authorization()
    assert "mock-api-key" not in str(error.value) and "private" not in str(error.value)
    assert len(calls) == 1 and calls[0]["follow_redirects"] is False and calls[0]["trust_env"] is False


def test_token_malformed_and_401_refresh(app, payment_setup, monkeypatch):
    gateway = ClickPesa(app.config)
    monkeypatch.setattr(gateway, "_request", Mock(return_value=["bad response"]))
    with pytest.raises(GatewayError):
        gateway._authorization()
    requests = Mock(side_effect=[{"success": True, "token": "first"}, GatewayError("credentials"), {"success": True, "token": "second"}, []])
    monkeypatch.setattr(gateway, "_request", requests)
    assert gateway.query_payment("TZABC123") == []
    assert requests.call_count == 4


def test_checksums_canonical_nested_unicode():
    payload = {"event": "PAYMENT RECEIVED", "data": {"z": [2, 1], "name": "Mwanafunzi wa Dar es Salaam — hesabu", "a": {"b": 2, "a": 1}}}
    for ascii_only in (True, False):
        payload["checksum"] = checksum(payload, "mock-checksum", ascii_only)
        assert verify_checksum(payload, "mock-checksum")
    payload["data"]["a"]["b"] = 3
    assert not verify_checksum(payload, "mock-checksum")


def test_invalid_payment_origin_config(app, monkeypatch):
    monkeypatch.setitem(app.config, "PAYMENT_RETURN_URL", "https://evil.test/payments/return")
    with pytest.raises(RuntimeError):
        configure_payments(app)


def test_decimal_catalogue_price_matches_display_and_order(app, db, payment_setup, payment_admin):
    app.extensions["payment_catalog"]["plans"]["payment_test"]["price"] = "1000.75"
    assert b"TZS 1,000.75" in payment_admin.get("/admin/payments").data
    start(payment_admin)
    with app.app_context():
        assert db.session.scalar(select(PaymentOrder)).amount == Decimal("1000.75")


def test_cli_redacts_keys_and_no_network(app, payment_setup):
    result = app.test_cli_runner().invoke(args=["payments-check"])
    assert result.exit_code == 0
    assert "CLICKPESA_API_KEY: configured" in result.output and "mock-api-key" not in result.output
    assert not payment_setup.queries and not payment_setup.created


def test_multiple_successes_fail_closed(app, db, payment_setup, payment_admin):
    from tzstudies.payments import verified_record
    start(payment_admin)
    with app.app_context():
        order = db.session.scalar(select(PaymentOrder))
        with pytest.raises(ConfirmationError):
            verified_record(order, [provider_record(order.order_reference), provider_record(order.order_reference, id="second", paymentReference="second")])


def test_registered_callbacks_have_expected_production_paths(app):
    assert urlsplit(app.config["PAYMENT_RETURN_URL"]).path == "/payments/return"
    assert urlsplit(app.config["CLICKPESA_WEBHOOK_URL"]).path == WEBHOOK


def test_webhook_during_checkout_creation_cannot_be_overwritten(app, db, payment_setup, payment_admin, monkeypatch):
    def immediate_confirmation(order):
        apply_confirmation(order.id, provider_record(order.order_reference))
        return "https://checkout.clickpesa.com/mock"
    monkeypatch.setattr(payment_setup, "create_checkout", immediate_confirmation)
    _, response = start(payment_admin)
    assert response.status_code == 303
    with app.app_context():
        order = db.session.scalar(select(PaymentOrder))
        assert order.status == "paid" and order.checkout_url is None and order.completed_at


def test_expired_intent_rejected(app, payment_setup, payment_admin, monkeypatch):
    from itsdangerous import URLSafeTimedSerializer
    from itsdangerous.timed import TimestampSigner
    class OldSigner(TimestampSigner):
        def get_timestamp(self):
            return 0
    with monkeypatch.context() as changed:
        changed.setattr("tzstudies.payments._signer", lambda: URLSafeTimedSerializer(app.secret_key, salt="tz-payment-intent-v1", signer=OldSigner))
        page = payment_admin.get("/admin/payments")
        token = re.search(rb'name="intent" value="([^"]+)"', page.data).group(1).decode()
    assert payment_admin.post("/payments/checkout/payment_test", data={"intent": token}).status_code == 400
    assert not payment_setup.created


def test_provider_post_timeout_is_not_retried(app, payment_setup, monkeypatch):
    gateway = ClickPesa(app.config)
    requests = Mock(side_effect=[{"success": True, "token": "mock-token"}, GatewayError()])
    monkeypatch.setattr(gateway, "_request", requests)
    with pytest.raises(GatewayError):
        gateway.create_checkout(Mock(amount=Decimal("1000"), order_reference="TZTEST", currency="TZS", plan_name="Test"))
    assert requests.call_count == 2


def test_custom_callback_urls_register_handlers(monkeypatch):
    from tzstudies import create_app
    from tzstudies.config import TestingConfig
    monkeypatch.setattr(TestingConfig, "PAYMENT_RETURN_URL", "https://mytzstudies.com/payments/custom-return")
    monkeypatch.setattr(TestingConfig, "CLICKPESA_WEBHOOK_URL", "https://mytzstudies.com/payments/custom-hook")
    local = create_app("testing")
    client = local.test_client()
    assert client.get("/payments/custom-return").status_code == 302
    assert client.post("/payments/custom-hook", json=notification(provider_record("TZUNKNOWN"))).status_code == 204
    assert client.post(WEBHOOK, json={}).status_code == 404
