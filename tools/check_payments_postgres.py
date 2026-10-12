"""Integration check restricted to the disposable local review cluster, never Supabase."""

import importlib.util
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.exc import DBAPIError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CLUSTER = ROOT / "tmp/analytics-postgres-review"
ADMIN_URL = "postgresql://analytics_review@127.0.0.1:55432/postgres"
admin_engine = sa.create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
with admin_engine.connect() as connection:
    if Path(connection.scalar(sa.text("SHOW data_directory"))).resolve() != CLUSTER.resolve():
        raise RuntimeError("This check requires the disposable workspace review cluster.")
    if not connection.scalar(sa.text("SELECT 1 FROM pg_database WHERE datname='paypal_review'")):
        connection.execute(sa.text("CREATE DATABASE paypal_review"))
admin_engine.dispose()
URL = "postgresql://analytics_review@127.0.0.1:55432/paypal_review"
engine = sa.create_engine(URL)
with engine.begin() as connection:
    for role in ("anon", "authenticated", "service_role"):
        if not connection.scalar(sa.text("SELECT 1 FROM pg_roles WHERE rolname=:role"), {"role": role}):
            connection.execute(
                sa.text(f"CREATE ROLE {role} NOLOGIN" + (" BYPASSRLS" if role == "service_role" else ""))
            )
    connection.execute(
        sa.text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role")
    )

from tzstudies.config import TestingConfig  # noqa: E402

TestingConfig.SQLALCHEMY_DATABASE_URI = URL
TestingConfig.PAYPAL_CLIENT_ID = "mock-client"
from tzstudies import create_app  # noqa: E402
from tzstudies.extensions import db  # noqa: E402
from tzstudies.models import User  # noqa: E402
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent  # noqa: E402
from tzstudies.payments import apply_confirmation, capture_payment  # noqa: E402
from tzstudies.security import hash_password  # noqa: E402

app = create_app("testing")
denied = 0
for role in ("anon", "authenticated"):
    for name in ("payment_order", "payment_webhook_event"):
        for sql in (
            f'SELECT * FROM "{name}" LIMIT 1',
            f'INSERT INTO "{name}" DEFAULT VALUES',
            f'UPDATE "{name}" SET id=id WHERE false',
            f'DELETE FROM "{name}" WHERE false',
        ):
            try:
                with engine.begin() as connection:
                    connection.execute(sa.text(f"SET LOCAL ROLE {role}"))
                    connection.execute(sa.text(sql))
            except DBAPIError as error:
                assert error.orig.pgcode == "42501"
                denied += 1
            else:
                raise AssertionError(f"Public role could access {name}")

# Exercise the upgrade on absent tables, then again on bootstrapped tables.
with app.app_context():
    db.session.remove()
    PaymentWebhookEvent.__table__.drop(db.engine)
    PaymentOrder.__table__.drop(db.engine)
spec = importlib.util.spec_from_file_location(
    "payment_migration", ROOT / "migrations/versions/bd74e902a631_add_private_payments.py"
)
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)
with engine.begin() as connection:
    migration.op = Operations(MigrationContext.configure(connection))
    migration.upgrade()
    migration.upgrade()
    assert connection.scalar(sa.text("SELECT relrowsecurity FROM pg_class WHERE relname='payment_order'"))
    assert not connection.scalar(sa.text("SELECT has_table_privilege('anon', 'payment_order', 'SELECT')"))
    connection.execute(sa.text("SET LOCAL ROLE service_role"))
    assert connection.scalar(sa.text("SELECT count(*) FROM payment_order")) == 0

# Add the provider fields to a historical schema, repeat safely, then start again.
spec = importlib.util.spec_from_file_location(
    "paypal_migration", ROOT / "migrations/versions/c912d34f5e60_paypal_orders.py"
)
new_migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(new_migration)
with engine.begin() as connection:
    new_migration.op = Operations(MigrationContext.configure(connection))
    new_migration.upgrade()
    new_migration.upgrade()

spec = importlib.util.spec_from_file_location("payment_mocks", ROOT / "tests/test_payments.py")
mocks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mocks)
gateway = mocks.MockGateway()
app.extensions["paypal"] = gateway
app.config["PAYMENTS_ENABLED"] = True
with app.app_context():
    user = db.session.scalar(sa.select(User).where(User.email == "payments-admin@example.test"))
    if user is None:
        user = User(
            name="Local payment admin",
            email="payments-admin@example.test",
            is_admin=True,
            pw_hash=hash_password("River stones remember sunrise!"),
        )
        db.session.add(user)
        db.session.flush()
    user_id = user.id
    plan = app.extensions["payment_catalog"]["plans"]["payment_test"]
    order = PaymentOrder(
        id="a" * 32,
        order_reference="TZ" + "A" * 32,
        user_id=user.id,
        intent_key="b" * 64,
        plan_id="payment_test",
        plan_name=plan["name"],
        plan_snapshot=plan,
        amount=1,
        currency="USD",
        status="pending",
        provider="paypal",
        provider_mode="sandbox",
    )
    response = gateway.create_checkout(order)
    order.provider_id = response["id"]
    order.provider_status = response["status"]
    db.session.add(order)
    db.session.commit()
gateway.approve()


def capture(_):
    from flask_login import login_user

    with app.test_request_context():
        login_user(db.session.get(User, user_id))
        return capture_payment("a" * 32)


with ThreadPoolExecutor(max_workers=4) as workers:
    list(workers.map(capture, range(8)))
assert len(gateway.captures) == 1
record = gateway.get_order("ORDER123456789")
capture_record = gateway.get_capture("CAPTURE1234567")
event = {"id": "WH-CONCURRENT", "event": "PAYMENT.CAPTURE.COMPLETED", "provider_id": "CAPTURE1234567"}


def confirm(_):
    with app.app_context():
        return apply_confirmation("a" * 32, record, capture_record, event)


with ThreadPoolExecutor(max_workers=4) as workers:
    outcomes = list(workers.map(confirm, range(8)))
assert outcomes.count("processed") == 1 and outcomes.count("duplicate") == 7
with app.app_context():
    db.session.expire_all()
    order = db.session.get(PaymentOrder, "a" * 32)
    assert order.status == "paid" and order.completed_at and db.session.query(PaymentWebhookEvent).count() == 1

result = {
    "postgres_version": 17,
    "public_operations_denied": denied,
    "concurrent_captures": 8,
    "provider_capture_requests": len(gateway.captures),
    "concurrent_callbacks": 8,
    "processed_receipts": 1,
    "migration_fresh_and_repeat": True,
    "service_role_access_preserved": True,
}
(ROOT / "tmp/payments-review").mkdir(parents=True, exist_ok=True)
(ROOT / "tmp/payments-review/postgres-checks.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
engine.dispose()
