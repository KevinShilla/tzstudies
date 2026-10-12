"""Loopback-only browser review with an isolated SQLite DB and mock gateway.

This is a developer tool, never an application route or production payment mode.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REVIEW = ROOT / "tmp/payments-review"
REVIEW.mkdir(parents=True, exist_ok=True)

from tzstudies.config import TestingConfig  # noqa: E402

TestingConfig.SQLALCHEMY_DATABASE_URI = "sqlite:///" + (REVIEW / "review.db").as_posix()
TestingConfig.PUBLIC_BASE_URL = "http://127.0.0.1:5052"
TestingConfig.PAYMENT_RETURN_URL = "http://127.0.0.1:5052/payments/return"
TestingConfig.PAYPAL_WEBHOOK_URL = "http://127.0.0.1:5052/payments/webhooks/paypal"
TestingConfig.PAYPAL_CLIENT_ID = "mock-client"
TestingConfig.PAYPAL_CLIENT_SECRET = "mock-secret"
TestingConfig.PAYPAL_WEBHOOK_ID = "mock-webhook"
TestingConfig.PAYPAL_MODE = "sandbox"
TestingConfig.PAYMENTS_ENABLED = True
TestingConfig.PAYMENT_TEST_PLAN_ENABLED = True
TestingConfig.WTF_CSRF_ENABLED = True
TestingConfig.ANALYTICS_ENABLED = False


from tzstudies import create_app  # noqa: E402
from tzstudies.extensions import db  # noqa: E402
from tzstudies.models import User  # noqa: E402
from tzstudies.security import hash_password  # noqa: E402

spec = importlib.util.spec_from_file_location("review_payment_mocks", ROOT / "tests/test_payments.py")
mocks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mocks)


app = create_app("testing")
app.extensions["paypal"] = mocks.MockGateway()
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(
        User(
            name="Review admin",
            email="admin@example.test",
            is_admin=True,
            pw_hash=hash_password("River stones remember sunrise!"),
        )
    )
    db.session.commit()
    from tzstudies.payment_models import PaymentOrder

    plan = app.extensions["payment_catalog"]["plans"]["payment_test"]
    user = db.session.query(User).one()
    order = PaymentOrder(
        id="e" * 32,
        order_reference="TZ" + "E" * 32,
        user_id=user.id,
        intent_key="e" * 64,
        plan_id="payment_test",
        plan_name=plan["name"],
        plan_snapshot=plan,
        amount=1,
        currency="USD",
        status="pending",
        provider="paypal",
        provider_mode="sandbox",
    )
    gateway = app.extensions["paypal"]
    response = gateway.create_checkout(order)
    order.provider_id = response["id"]
    order.checkout_url = response["links"][0]["href"]
    db.session.add(order)
    db.session.commit()
    gateway.approve()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5052, debug=False, use_reloader=False)
