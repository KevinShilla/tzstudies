"""Loopback-only browser review with an isolated SQLite DB and mock gateway.

This is a developer tool, never an application route or production payment mode.
"""
import json
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
TestingConfig.CLICKPESA_WEBHOOK_URL = "http://127.0.0.1:5052/payments/webhooks/clickpesa"
TestingConfig.CLICKPESA_CLIENT_ID = "mock-client"
TestingConfig.CLICKPESA_API_KEY = "mock-api-key"
TestingConfig.CLICKPESA_CHECKSUM_KEY = "mock-checksum"
TestingConfig.PAYMENTS_ENABLED = True
TestingConfig.PAYMENT_TEST_PLAN_ENABLED = True
TestingConfig.WTF_CSRF_ENABLED = True
TestingConfig.ANALYTICS_ENABLED = False

from tzstudies import create_app  # noqa: E402
from tzstudies.extensions import db  # noqa: E402
from tzstudies.models import User  # noqa: E402
from tzstudies.security import hash_password  # noqa: E402


class ReviewGateway:
    def create_checkout(self, order):
        return "https://checkout.clickpesa.com/mock/" + order.order_reference

    def query_payment(self, reference):
        path = REVIEW / "provider-state.json"
        if path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["orderReference"] == reference:
                return [record]
        return []


app = create_app("testing")
app.extensions["clickpesa"] = ReviewGateway()
with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.add(User(name="Review admin", email="admin@example.test", is_admin=True,
                        pw_hash=hash_password("River stones remember sunrise!")))
    db.session.commit()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5052, debug=False, use_reloader=False)
