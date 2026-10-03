import html
import importlib.util
import re
import secrets
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.exc import IntegrityError, OperationalError

from tzstudies import analytics
from tzstudies.analytics_models import AnalyticsEvent as Event
from tzstudies.analytics_models import AnalyticsPageView as View
from tzstudies.analytics_models import AnalyticsVisit as Visit
from tzstudies.analytics_models import AnalyticsVisitor as Visitor
from tzstudies.analytics_reports import report
from tzstudies.models import User
from tzstudies.security import hash_password

PASSWORD = "River stones remember sunrise!"


def ticket(client, path="/", headers=None):
    response = client.get(path, headers=headers or {})
    assert response.status_code == 200
    match = re.search(rb'<meta name="analytics-ticket" content="([^"]+)"', response.data)
    assert match
    return html.unescape(match.group(1).decode())


def send(client, token, **kwargs):
    return client.post("/analytics/collect", json={"ticket": token, **kwargs})


def event(name, label="signup_form", identifier=None):
    return {"id": identifier or secrets.token_hex(8), "name": name, "label": label}


def snapshot(app, **args):
    with app.test_request_context("/admin/analytics/data"):
        return report(args)


@pytest.fixture
def admin_client(client, app, db):
    with app.app_context():
        db.session.add(User(name="Local test admin", email="admin@example.test", pw_hash=hash_password(PASSWORD), is_admin=True))
        db.session.commit()
    assert client.post("/login", data={"email": "admin@example.test", "password": PASSWORD}).status_code == 302
    return client


def test_dashboard_is_private(client, auth_client):
    anonymous = client.application.test_client()
    for path in ("/admin/analytics", "/admin/analytics/data"):
        assert anonymous.get(path).status_code == 302
        assert auth_client.get(path).status_code == 403


def test_admin_sees_dashboard_and_does_not_inflate_traffic(admin_client, app):
    assert b"Your website, at a glance" in admin_client.get("/admin/analytics").data
    page = admin_client.get("/")
    assert b'content="' in page.data and b'analytics-ticket' not in page.data
    response = admin_client.get("/admin/analytics/data")
    assert response.status_code == 200 and response.get_json()["summary"]["views"] == 0
    assert "no-store" in response.headers["Cache-Control"]
    with app.app_context():
        assert User.query.filter_by(is_admin=True).count() == 1


def test_views_are_idempotent_and_visitors_distinct(client, app):
    first = ticket(client)
    assert send(client, first).status_code == 204
    assert send(client, first).status_code == 204
    assert send(client, ticket(client, "/about")).status_code == 204
    other = app.test_client()
    assert send(other, ticket(other)).status_code == 204
    data = snapshot(app)
    assert data["summary"]["views"] == 3
    assert data["summary"]["visitors"] == 2
    assert data["summary"]["visits"] == 2
    assert data["summary"]["new_visitors"] == 2
    assert next(row for row in data["pages"] if row["path"] == "/")["views"] == 2
    assert any(row["views"] == 0 for row in data["pages"])


def test_restored_page_is_a_new_idempotent_view(client, app):
    token = ticket(client)
    send(client, token)
    send(client, ticket(client, "/about"))
    restored = secrets.token_hex(8)
    send(client, token, occurrence=restored)
    send(client, token, occurrence=restored)
    result = snapshot(app)
    assert result["summary"]["views"] == 3 and result["summary"]["visits"] == 1
    assert [row["path"] for row in result["journeys"][0]["pages"]] == ["/", "/about", "/"]


def test_errors_and_sensitive_routes_never_offer_tracking(client):
    ticket(client)
    for path in ("/view/not-a-real-exam.pdf", "/not-found", "/forgot-password", "/privacy"):
        assert b"analytics-ticket" not in client.get(path).data


@pytest.mark.parametrize("url,referrer,source,channel,host", [
    ("/", "", "Direct", "direct", ""),
    ("/", "https://www.google.com/search?q=private", "Google", "search", "google.com"),
    ("/", "https://www.google.co.tz/search?q=test", "Google", "search", "google.co.tz"),
    ("/?utm_source=youtube&utm_medium=social", "", "YouTube", "social", ""),
    ("/?utm_source=instagram", "https://www.google.com/", "Instagram", "social", "google.com"),
    ("/", "https://l.instagram.com/?u=private", "Instagram", "social", "l.instagram.com"),
    ("/", "https://school.example.org/people/private?email=hidden", "school.example.org", "referral", "school.example.org"),
    ("/?utm_source=someone%40example.com", "", "Other campaign", "campaign", ""),
    ("/", "https://user:secret@external.example.org/", "Direct", "direct", ""),
    ("/", "https://mytzstudies.com/about", "Direct", "direct", ""),
])
def test_sources_are_recognised_and_sanitised(client, app, url, referrer, source, channel, host):
    assert send(client, ticket(client, url, {"Referer": referrer})).status_code == 204
    assert send(client, ticket(client, "/about", {"Referer": "http://localhost/"})).status_code == 204
    row = snapshot(app)["sources"][0]
    assert (row["source"], row["channel"], row["referrer"]) == (source, channel, host)
    assert row["views"] == 2
    with app.app_context():
        assert "?" not in View.query.first().path


def test_entry_exit_order_and_active_time_with_reordered_beacons(client, app, monkeypatch):
    first = ticket(client)
    send(client, first)
    second = ticket(client, "/about")
    send(client, second)
    now = analytics.now_utc()
    monkeypatch.setattr(analytics, "now_utc", lambda: now + timedelta(seconds=60))
    assert send(client, second, seconds=40, state="ended", sequence=3).status_code == 204
    send(client, second, seconds=5, state="active", sequence=2)
    send(client, first, seconds=20, state="ended", sequence=4)
    data = snapshot(app)
    assert data["entries"][0]["path"] == "/"
    assert data["exits"][0]["path"] == "/about"
    about = next(row for row in data["pages"] if row["path"] == "/about")
    assert about["average_time"] == 40 and about["exit_rate"] == 100
    assert data["journeys"][0]["pages"][0]["path"] == "/"
    assert data["transitions"][0]["to"] == "/about"


def test_inactive_visit_gets_exit_without_a_browser_beacon(client, app, db):
    send(client, ticket(client))
    with app.app_context():
        Visit.query.first().last_seen = analytics.now_utc() - timedelta(minutes=31)
        db.session.commit()
    assert snapshot(app)["exits"][0]["path"] == "/"


def test_returning_browser_has_new_session(client, app, db):
    send(client, ticket(client))
    with app.app_context():
        visitor = Visitor.query.first()
        visitor.first_seen = analytics.now_utc() - timedelta(days=40)
        db.session.commit()
    client.delete_cookie(analytics.VISIT_COOKIE)
    send(client, ticket(client, "/about"))
    result = snapshot(app)
    assert result["summary"]["visitors"] == 1
    assert result["summary"]["visits"] == 2
    assert result["summary"]["returning_visitors"] == 1 and result["summary"]["new_visitors"] == 0
    with app.app_context():
        assert Visit.query.order_by(Visit.started_at.desc()).first().is_returning


def test_signup_is_server_confirmed_attributed_and_funnel_ordered(client, app):
    send(client, ticket(client, "/?utm_source=youtube"))
    send(client, ticket(client, "/answer_keys"))
    signup = ticket(client, "/signup")
    send(client, signup, events=[event("signup_start"), event("signup_leave")])
    response = client.post("/signup", data={"name": "Student", "email": "student@example.test", "password": PASSWORD, "analytics_ticket": signup})
    assert response.status_code == 302
    result = snapshot(app)
    assert result["summary"]["signups"] == result["summary"]["tracked_signups"] == 1
    assert result["summary"]["conversion"] == 100 and result["summary"]["signup_abandoned"] == 0
    assert [row["count"] for row in result["funnel"]] == [1, 1, 1, 1]
    assert result["signup_pages"][0]["path"] == "/answer_keys"
    assert result["sources"][0]["source"] == "YouTube" and result["sources"][0]["signups"] == 1
    assert result["calendar"]["today"]["signups"] == 1
    assert sum(row["signups"] for row in result["trend"]["points"]) == 1
    assert "student@example.test" not in str(result) and "Student" not in str(result)


def test_failed_signup_does_not_count_completion_and_abandonment_is_tracked(client, app):
    token = ticket(client, "/signup")
    send(client, token, events=[event("signup_start"), event("signup_leave")])
    client.post("/signup", data={"name": "Student", "email": "invalid", "password": "bad", "analytics_ticket": token})
    result = snapshot(app)
    assert result["summary"]["signups"] == result["summary"]["tracked_signups"] == 0
    assert result["summary"]["signup_starts"] == result["summary"]["signup_abandoned"] == 1


def test_navigation_away_from_signup_records_abandonment_without_exit_beacon(client, app):
    token = ticket(client, "/signup")
    send(client, token, events=[event("signup_start")])
    send(client, ticket(client, "/about"))
    assert snapshot(app)["summary"]["signup_abandoned"] == 1


def test_login_success_and_safe_engagement_events(client, sample_user, app):
    token = ticket(client, "/login")
    send(client, token, events=[event("button_click", "login"), event("search", "library_search")])
    client.post("/login", data={"email": "test@example.com", "password": "password123", "analytics_ticket": token})
    rows = snapshot(app)["event_counts"]
    assert any(row["name"] == "login" and row["count"] == 1 for row in rows)
    assert any(row["name"] == "search" for row in rows)


def test_failed_login_render_is_tracked_and_login_can_continue(client, sample_user, app):
    first = ticket(client, "/login")
    send(client, first)
    failed = client.post("/login", data={"email": "test@example.com", "password": "wrong", "analytics_ticket": first})
    assert failed.status_code == 200
    second = html.unescape(re.search(rb'name="analytics-ticket" content="([^"]+)"', failed.data).group(1).decode())
    send(client, second)
    client.post("/login", data={"email": "test@example.com", "password": "password123", "analytics_ticket": second})
    result = snapshot(app)
    assert result["summary"]["views"] == 2 and result["summary"]["visits"] == 1
    assert next(row for row in result["event_counts"] if row["name"] == "login")["count"] == 1


def test_reforged_or_stolen_ticket_and_cross_origin_are_rejected(client, app):
    token = ticket(client)
    assert send(client, token + "bad").status_code == 400
    thief = app.test_client()
    ticket(thief)
    assert send(thief, token).status_code == 400
    assert client.post("/analytics/collect", json={"ticket": token}, headers={"Origin": "https://untrusted.example"}).status_code == 403


@pytest.mark.parametrize("payload", [
    {"seconds": -1}, {"seconds": True}, {"seconds": 14401}, {"state": []}, {"sequence": "1"},
    {"events": [event("signup_complete")]}, {"events": [event("login")]},
    {"events": [{"id": "x", "name": "search", "label": "library_search"}]},
    {"events": [{"id": "a" * 16, "name": [], "label": "library_search"}]},
    {"events": [event("search", "user@example.com")]}, {"email": "private@example.com"},
    {"events": [event("search", "library_search")] * 13},
])
def test_malformed_or_sensitive_payloads_are_rejected(client, payload):
    assert send(client, ticket(client), **payload).status_code == 400


def test_beacon_csrf_is_enforced_and_valid_formdata_works(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)
    response = client.get("/")
    token = html.unescape(re.search(rb'name="analytics-ticket" content="([^"]+)"', response.data).group(1).decode())
    csrf = html.unescape(re.search(rb'name="csrf-token" content="([^"]+)"', response.data).group(1).decode())
    assert send(client, token).status_code == 400
    import json
    assert client.post("/analytics/collect", data={"csrf_token": csrf, "payload": json.dumps({"ticket": token})}).status_code == 204


@pytest.mark.parametrize("headers", [{"DNT": "1"}, {"Sec-GPC": "1"}, {"User-Agent": "Googlebot"}])
def test_privacy_signals_and_bots_are_excluded(client, app, headers):
    response = client.get("/", headers=headers)
    assert b"analytics-ticket" not in response.data
    assert not any(analytics.VISITOR_COOKIE in value for value in response.headers.getlist("Set-Cookie"))
    assert snapshot(app)["summary"]["views"] == 0


def test_opt_out_does_not_break_signup_or_login(client, app):
    token = ticket(client)
    send(client, token)
    assert client.post("/analytics/preferences", data={"choice": "off"}).status_code == 302
    assert b"analytics-ticket" not in client.get("/signup").data
    client.post("/signup", data={"name": "Private Student", "email": "private@example.test", "password": PASSWORD})
    assert snapshot(app)["summary"]["signups"] == 1
    assert snapshot(app)["summary"]["tracked_signups"] == 0
    assert client.get("/history").status_code == 200
    client.post("/analytics/preferences", data={"choice": "on"})
    assert b"analytics-ticket" in client.get("/").data


def test_tracking_failure_does_not_undo_account_creation(client, app, monkeypatch):
    token = ticket(client, "/signup")
    def unavailable(*args, **kwargs):
        raise OperationalError("analytics", {}, Exception("unavailable"))
    monkeypatch.setattr(analytics, "Session", unavailable)
    assert send(client, token).status_code == 503
    assert client.post("/signup", data={"name": "Student", "email": "working@example.test", "password": PASSWORD, "analytics_ticket": token}).status_code == 302
    with app.app_context():
        assert User.query.count() == 1
    assert client.get("/history").status_code == 200


def test_signup_conversion_survives_an_initial_collection_race(client, app, monkeypatch):
    token = ticket(client, "/signup")
    original = analytics._ensure_page
    attempts = []
    def race(store, data, now):
        attempts.append(1)
        if len(attempts) == 1:
            raise IntegrityError("concurrent initial page", {}, Exception("duplicate"))
        return original(store, data, now)
    monkeypatch.setattr(analytics, "_ensure_page", race)
    assert client.post("/signup", data={"name": "Student", "email": "race@example.test", "password": PASSWORD, "analytics_ticket": token}).status_code == 302
    result = snapshot(app)
    assert len(attempts) == 2
    assert result["summary"]["signups"] == result["summary"]["tracked_signups"] == 1


def test_date_boundaries_comparisons_and_historical_signup_totals(client, app, db):
    # 21:30 UTC is already the next day in Tanzania.
    send(client, ticket(client))
    with app.app_context():
        view = View.query.first()
        view.created_at = datetime(2026, 9, 20, 21, 30)
        view.local_day = analytics.local_day(view.created_at)
        Visitor.query.first().first_seen = view.created_at
        db.session.add(User(name="Historical", email="historical@example.test", pw_hash=hash_password(PASSWORD), created_at=datetime(2026, 9, 20, 21, 30)))
        db.session.commit()
    result = snapshot(app, period="custom", start="2026-09-21", end="2026-09-21")
    assert result["summary"]["views"] == result["summary"]["signups"] == 1
    assert result["unattributed_signups"] == 1
    assert result["trend"]["points"] == [{"date": "2026-09-21", "visitors": 1, "views": 1, "signups": 1}]
    next_day = snapshot(app, period="custom", start="2026-09-22", end="2026-09-22")
    assert next_day["summary"]["views"] == 0
    assert next_day["comparison"]["views"]["previous"] == 1
    assert next_day["comparison"]["views"]["change"] == -100
    assert snapshot(app, period="all")["totals"]["signups"] == 1


@pytest.mark.parametrize("query", ["period=invalid", "period=custom", "period=custom&start=2026-09-25&end=2026-09-24", "period=custom&start=2026-09-01&end=2099-01-01"])
def test_invalid_date_filters_return_clear_errors(admin_client, query):
    response = admin_client.get("/admin/analytics/data?" + query)
    assert response.status_code == 400 and "error" in response.get_json()


@pytest.mark.parametrize("period", ["today", "7d", "30d", "month", "all"])
def test_all_date_presets_and_empty_chart(admin_client, period):
    result = admin_client.get("/admin/analytics/data?period=" + period).get_json()
    assert result["range"]["period"] == period
    assert result["trend"]["points"] and result["summary"]["visitors"] == 0
    assert result["comparison"] is None if period == "all" else result["comparison"] is not None


def test_pruning_keeps_user_accounts(client, app, db):
    send(client, ticket(client, "/answer_keys"))
    with app.app_context():
        old = analytics.now_utc() - timedelta(days=400)
        Visit.query.first().last_seen = old
        Visitor.query.first().last_seen = old
        db.session.add(User(name="Keep", email="keep@example.test", pw_hash=hash_password(PASSWORD)))
        db.session.commit()
    result = app.test_cli_runner().invoke(args=["analytics-prune"])
    assert result.exit_code == 0
    with app.app_context():
        assert Visit.query.count() == View.query.count() == Event.query.count() == Visitor.query.count() == 0
        assert User.query.count() == 1


def test_migration_is_complete_and_bootstrap_compatible():
    path = Path(__file__).resolve().parents[1] / "migrations/versions/a43809df725c_add_private_analytics.py"
    spec = importlib.util.spec_from_file_location("analytics_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        User.__table__.create(connection)
        migration.op = Operations(MigrationContext.configure(connection))
        migration.upgrade()
        migration.upgrade()
        inspector = sa.inspect(connection)
        for model in (Visitor, Visit, View, Event):
            assert {column["name"] for column in inspector.get_columns(model.__tablename__)} == set(model.__table__.columns.keys())
        migration.downgrade()
        assert sa.inspect(connection).get_table_names() == ["user"]


@pytest.mark.parametrize("roles", [[], ["anon", "authenticated"]])
def test_postgres_bootstrap_enables_rls_and_revokes_public_admin_authority(roles):
    class Connection:
        dialect = type("Dialect", (), {"name": "postgresql"})()
        def __init__(self):
            self.statements = []
        def execute(self, statement):
            self.statements.append(str(statement))
            return self
        def scalars(self):
            return roles
    connection = Connection()
    analytics.protect_postgres_tables(connection)
    protections = [statement for statement in connection.statements if "ENABLE ROW LEVEL SECURITY" in statement]
    assert len(protections) == 7
    assert 'ALTER TABLE "user" ENABLE ROW LEVEL SECURITY' in protections
    revocations = [statement for statement in connection.statements if statement.startswith("REVOKE ALL")]
    assert len(revocations) == 7 * (len(roles) + 1)
    assert 'REVOKE ALL ON TABLE "user" FROM PUBLIC' in revocations
    assert not any("service_role" in statement for statement in revocations)
