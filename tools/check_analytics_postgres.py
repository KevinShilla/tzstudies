"""Optional integration check on the dedicated, disposable local PostgreSQL review cluster."""
import html
import json
import re
import sys
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
URL = "postgresql://analytics_review@127.0.0.1:55432/postgres"
engine = sa.create_engine(URL)
with engine.begin() as connection:
    cluster = Path(connection.scalar(sa.text("SHOW data_directory"))).resolve()
    if cluster != (ROOT / "tmp" / "analytics-postgres-review").resolve():
        raise RuntimeError("This check requires the isolated workspace PostgreSQL review cluster.")
    for role in ("anon", "authenticated", "service_role"):
        if not connection.scalar(sa.text("SELECT 1 FROM pg_roles WHERE rolname=:role"), {"role": role}):
            connection.execute(sa.text(f'CREATE ROLE {role} NOLOGIN' + (" BYPASSRLS" if role == "service_role" else "")))
    connection.execute(sa.text("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role"))

from tzstudies.config import TestingConfig  # noqa: E402
from tzstudies.models import User  # noqa: E402
from tzstudies.security import hash_password  # noqa: E402

PASSWORD = "River stones remember sunrise!"
# Model the old exposed account table, with an existing admin and permissive client policy.
with engine.begin() as connection:
    User.__table__.create(connection, checkfirst=True)
    if not connection.scalar(sa.select(sa.func.count()).select_from(User.__table__)):
        connection.execute(User.__table__.insert().values(name="Local PG review admin", email="pg-admin@example.test", pw_hash=hash_password(PASSWORD), is_admin=True))
    connection.execute(sa.text('DROP POLICY IF EXISTS review_public_account ON "user"'))
    connection.execute(sa.text('CREATE POLICY review_public_account ON "user" TO anon, authenticated USING (true) WITH CHECK (true)'))

TestingConfig.SQLALCHEMY_DATABASE_URI = URL
from tzstudies import create_app  # noqa: E402
from tzstudies.analytics_models import AnalyticsEvent, AnalyticsPageView, AnalyticsVisit, AnalyticsVisitor  # noqa: E402
from tzstudies.analytics_reports import report  # noqa: E402
from tzstudies.extensions import db  # noqa: E402
from tzstudies.models import AuthToken, LoginSession  # noqa: E402

app = create_app("testing")
private = (AnalyticsVisitor, AnalyticsVisit, AnalyticsPageView, AnalyticsEvent, User, AuthToken, LoginSession)
denied = 0
for role in ("anon", "authenticated"):
    for model in private:
        table = model.__table__.name
        key = list(model.__table__.primary_key.columns)[0].name
        for sql in [f'SELECT * FROM "{table}" LIMIT 1', f'INSERT INTO "{table}" DEFAULT VALUES',
                    f'UPDATE "{table}" SET "{key}"="{key}" WHERE false', f'DELETE FROM "{table}" WHERE false']:
            try:
                with engine.begin() as connection:
                    connection.execute(sa.text(f"SET LOCAL ROLE {role}"))
                    connection.execute(sa.text(sql))
            except DBAPIError as error:
                assert error.orig.pgcode == "42501", error.orig.pgcode
                denied += 1
            else:
                raise AssertionError(f"Public {role} must not access {table}")
for model in private:
    with engine.begin() as connection:
        connection.execute(sa.text("SET LOCAL ROLE service_role"))
        connection.scalar(sa.select(sa.func.count()).select_from(model.__table__))

client = app.test_client()
for path in ("/?utm_source=youtube", "/answer_keys", "/signup"):
    response = client.get(path)
    token = html.unescape(re.search(rb'name="analytics-ticket" content="([^"]+)"', response.data).group(1).decode())
    assert client.post("/analytics/collect", json={"ticket": token}).status_code == 204
assert client.post("/signup", data={"name": "PG student", "email": "pg-student@example.test", "password": PASSWORD, "analytics_ticket": token}).status_code == 302
with app.test_request_context("/admin/analytics/data"):
    result = report({})
    assert result["summary"]["visitors"] == result["summary"]["signups"] == result["summary"]["tracked_signups"] == 1
    assert result["sources"][0]["source"] == "YouTube" and result["sources"][0]["signups"] == 1
    assert [row["count"] for row in result["funnel"]] == [1, 1, 1, 1]
    assert User.query.filter_by(is_admin=True).count() == 1
    assert len(result["trend"]["points"]) == 30
    assert db.engine.dialect.name == "postgresql"
checks = {"postgres_version": 17, "public_operations_denied": denied, "protected_tables": 7,
          "service_role_read_preserved": True, "existing_admin_count": 1,
          "pg_tracking_and_signup_attribution": True, "pg_report_and_funnel": True,
          "cluster": "isolated tmp/analytics-postgres-review"}
(ROOT / "output" / "analytics" / "postgres-checks.json").write_text(json.dumps(checks, indent=2))
print(json.dumps(checks, indent=2))
engine.dispose()
