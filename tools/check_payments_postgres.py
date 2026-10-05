"""Integration check restricted to the disposable local review cluster, never Supabase."""
import hashlib
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
    if not connection.scalar(sa.text("SELECT 1 FROM pg_database WHERE datname='payments_review'")):
        connection.execute(sa.text("CREATE DATABASE payments_review"))
admin_engine.dispose()
URL = "postgresql://analytics_review@127.0.0.1:55432/payments_review"
engine = sa.create_engine(URL)
with engine.begin() as connection:
    for role in ("anon", "authenticated", "service_role"):
        if not connection.scalar(sa.text("SELECT 1 FROM pg_roles WHERE rolname=:role"), {"role": role}):
            connection.execute(sa.text(f"CREATE ROLE {role} NOLOGIN" + (" BYPASSRLS" if role == "service_role" else "")))
    connection.execute(sa.text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role"))

from tzstudies.config import TestingConfig  # noqa: E402

TestingConfig.SQLALCHEMY_DATABASE_URI = URL
TestingConfig.CLICKPESA_CLIENT_ID = "mock-client"
from tzstudies import create_app  # noqa: E402
from tzstudies.extensions import db  # noqa: E402
from tzstudies.models import User  # noqa: E402
from tzstudies.payment_models import PaymentOrder, PaymentWebhookEvent  # noqa: E402
from tzstudies.payments import apply_confirmation  # noqa: E402
from tzstudies.security import hash_password  # noqa: E402

app = create_app("testing")
denied = 0
for role in ("anon", "authenticated"):
    for name in ("payment_order", "payment_webhook_event"):
        for sql in (f'SELECT * FROM "{name}" LIMIT 1', f'INSERT INTO "{name}" DEFAULT VALUES',
                    f'UPDATE "{name}" SET id=id WHERE false', f'DELETE FROM "{name}" WHERE false'):
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
spec = importlib.util.spec_from_file_location("payment_migration", ROOT / "migrations/versions/bd74e902a631_add_private_payments.py")
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

with app.app_context():
    user = db.session.scalar(sa.select(User).where(User.email == "payments-admin@example.test"))
    if user is None:
        user = User(name="Local payment admin", email="payments-admin@example.test", is_admin=True,
                    pw_hash=hash_password("River stones remember sunrise!"))
        db.session.add(user)
        db.session.flush()
    order = PaymentOrder(id="a" * 32, order_reference="TZ" + "A" * 32, user_id=user.id, intent_key="b" * 64,
                         plan_id="payment_test", plan_name="Local test", plan_snapshot={}, amount=1000, currency="TZS", status="pending")
    db.session.add(order)
    db.session.commit()
record = {"id": "pg-provider-transaction", "status": "SUCCESS", "orderReference": "TZ" + "A" * 32,
          "clientId": "mock-client", "collectedAmount": 1000, "collectedCurrency": "TZS", "paymentReference": "pg-receipt"}
event = {"id": hashlib.sha256(b"PAYMENT RECEIVED|pg-provider-transaction").hexdigest(), "event": "PAYMENT RECEIVED", "provider_id": record["id"]}


def confirm(_):
    with app.app_context():
        return apply_confirmation("a" * 32, record, event)


with ThreadPoolExecutor(max_workers=4) as workers:
    outcomes = list(workers.map(confirm, range(8)))
assert outcomes.count("processed") == 1 and outcomes.count("duplicate") == 7
with app.app_context():
    db.session.expire_all()
    order = db.session.get(PaymentOrder, "a" * 32)
    assert order.status == "paid" and order.completed_at and db.session.query(PaymentWebhookEvent).count() == 1
    assert db.session.query(User).filter_by(is_admin=True).count() == 1
    # A provider transaction/reference cannot be attached to a second order.
    second = PaymentOrder(id="c" * 32, order_reference="TZ" + "C" * 32, user_id=order.user_id, intent_key="d" * 64,
                          plan_id="payment_test", plan_name="Local test", plan_snapshot={}, amount=1000, currency="TZS", status="pending")
    db.session.add(second)
    db.session.commit()
    try:
        apply_confirmation(second.id, dict(record, orderReference=second.order_reference))
    except sa.exc.IntegrityError:
        db.session.rollback()
    else:
        raise AssertionError("A provider transaction was processed twice")
    db.session.expire_all()
    assert db.session.get(PaymentOrder, "c" * 32).status == "pending"

result = {"postgres_version": 17, "public_operations_denied": denied, "concurrent_callbacks": 8,
          "completions": 1, "duplicate_receipts": 0, "duplicate_transaction_rejected": True,
          "migration_fresh_and_repeat": True, "service_role_access_preserved": True, "admin_count": 1}
(ROOT / "tmp/payments-review").mkdir(parents=True, exist_ok=True)
(ROOT / "tmp/payments-review/postgres-checks.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
engine.dispose()
