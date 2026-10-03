"""Signed, privacy-conscious analytics, isolated from normal app transactions."""

import hashlib
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

import click
from flask import before_render_template, current_app, g, request
from flask_login import current_user
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import delete, exists, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from tzstudies.analytics_models import AnalyticsEvent, AnalyticsPageView, AnalyticsVisit, AnalyticsVisitor
from tzstudies.extensions import db

VISITOR_COOKIE = "tz_visitor"
VISIT_COOKIE = "tz_visit"
OPTOUT_COOKIE = "tz_analytics_off"
COOKIE_AGE = 90 * 86400
PAGES = {
    "papers.index": ("Past papers", False, ""),
    "papers.answer_keys_page": ("Answer keys", True, "answer_keys"),
    "papers.view_exam": ("Exam paper", True, "exam_reader"),
    "papers.view_key": ("Worked answer key", True, "answer_key_reader"),
    "papers.paper_detail": ("Paper discussion", True, "discussion"),
    "papers.search": ("Search results", True, "paper_search"),
    "papers.history": ("My papers", True, "saved_papers"),
    "papers.about": ("Our story", False, ""),
    "auth.signup": ("Create account", False, ""),
    "auth.login": ("Log in", False, ""),
    "tutors.tutors_page": ("Find tutors", True, "tutor_directory"),
    "tutors.become_tutor": ("Become a tutor", True, "tutor_application"),
    "upload.upload_exams": ("Upload exams", True, "exam_upload"),
}
CLIENT_EVENTS = {"signup_start", "signup_leave", "button_click", "search", "feature_use"}
LABELS = {
    "signup_form", "signup_submit", "library_search", "library_filter", "tutor_filter",
    "open_exam", "open_key", "download_exam", "download_key", "browse_papers", "browse_keys",
    "find_tutors", "tutor_contact", "study_assistant", "start_signup", "login", "navigation",
    "discussion", "exam_upload", "tutor_application", "install_app",
}
SOCIAL = {
    "youtube": "YouTube", "youtu.be": "YouTube", "youtube.com": "YouTube",
    "instagram": "Instagram", "instagram.com": "Instagram", "facebook": "Facebook",
    "facebook.com": "Facebook", "fb.com": "Facebook", "tiktok": "TikTok", "tiktok.com": "TikTok",
    "twitter": "X / Twitter", "twitter.com": "X / Twitter", "x": "X / Twitter", "x.com": "X / Twitter",
    "t.co": "X / Twitter", "linkedin": "LinkedIn", "linkedin.com": "LinkedIn",
    "whatsapp": "WhatsApp", "whatsapp.com": "WhatsApp", "telegram": "Telegram", "t.me": "Telegram",
    "reddit": "Reddit", "reddit.com": "Reddit", "pinterest": "Pinterest", "pinterest.com": "Pinterest",
}


def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def local_day(value):
    return value.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=3))).date()


def _epoch(value):
    return value.replace(tzinfo=timezone.utc).timestamp()


def _signer(salt):
    return URLSafeTimedSerializer(current_app.secret_key, salt="tz-analytics-" + salt)


def _digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _read_cookie(name, salt, max_age):
    value = request.cookies.get(name, "")
    if len(value) > 2400:
        return None
    try:
        return _signer(salt).loads(value, max_age=max_age)
    except BadSignature:
        return None


def tracking_allowed():
    return (current_app.config["ANALYTICS_ENABLED"]
            and request.cookies.get(OPTOUT_COOKIE) != "1"
            and request.headers.get("DNT") != "1" and request.headers.get("Sec-GPC") != "1"
            and not (current_user.is_authenticated and current_user.is_admin)
            and not re.search(r"bot|crawler|spider|headless|preview|facebookexternalhit", request.user_agent.string, re.I))


def safe_host(value):
    """Keep a public hostname only. Drop private addresses, credentials, paths and queries."""
    if not isinstance(value, str) or len(value) > 2000:
        return ""
    try:
        parts = urlsplit(value)
        host = (parts.hostname or "").lower().rstrip(".")
        if parts.scheme not in ("https", "http") or parts.username or parts.password:
            return ""
        if not re.fullmatch(r"[a-z0-9.-]{1,253}", host) or "." not in host or re.fullmatch(r"[0-9.]+", host):
            return ""
        if host.endswith((".local", ".localhost", ".internal")):
            return ""
        return host.removeprefix("www.")
    except ValueError:
        return ""


def traffic_source(referrer, utm_source="", utm_medium=""):
    host = safe_host(referrer)
    own_hosts = {safe_host(current_app.config["PUBLIC_BASE_URL"]), safe_host(request.host_url)}
    if host in own_hosts:
        host = ""
    # Campaign labels are deliberately an allowlist: arbitrary UTM values can contain personal data.
    source = utm_source.lower().strip() if isinstance(utm_source, str) and len(utm_source) <= 60 else ""
    search_sources = {"google": "Google", "bing": "Bing", "duckduckgo": "DuckDuckGo",
                      "yahoo": "Yahoo", "ecosia": "Ecosia", "baidu": "Baidu"}
    if source in SOCIAL:
        return SOCIAL[source], "social", host
    if source in search_sources:
        return search_sources[source], "search", host
    if source in {"newsletter", "email"}:
        return "Email", "email", host
    for domain, label in SOCIAL.items():
        if host == domain or host.endswith("." + domain):
            return label, "social", host
    for domain, label in [("google", "Google"), ("bing", "Bing"), ("duckduckgo", "DuckDuckGo"),
                          ("yahoo", "Yahoo"), ("ecosia", "Ecosia"), ("baidu", "Baidu")]:
        if re.fullmatch(r"(?:[a-z0-9-]+\.)*" + domain + r"\.[a-z.]{2,20}", host):
            return label, "search", host
    if host:
        return host[:120], "referral", host
    if source or (isinstance(utm_medium, str) and utm_medium.lower() in {"social", "referral", "cpc", "email"}):
        return "Other campaign", "campaign", ""
    return "Direct", "direct", ""


def _prepare_page():
    g.analytics = None
    rendered_login = request.method == "POST" and request.endpoint == "auth.login"
    if (request.method != "GET" and not rendered_login) or request.endpoint not in PAGES or len(request.path) > 300 or not tracking_allowed():
        return
    now = now_utc()
    visitor_raw = _read_cookie(VISITOR_COOKIE, "visitor", COOKIE_AGE)
    if not isinstance(visitor_raw, str) or not re.fullmatch(r"[a-f0-9]{32}", visitor_raw):
        visitor_raw = secrets.token_hex(16)
    visit = _read_cookie(VISIT_COOKIE, "visit", current_app.config["ANALYTICS_SESSION_SECONDS"])
    if not isinstance(visit, dict) or visit.get("visitor") != _digest(visitor_raw):
        source, channel, referrer = traffic_source(request.referrer or "", request.args.get("utm_source", ""), request.args.get("utm_medium", ""))
        visit = {"id": secrets.token_hex(16), "visitor": _digest(visitor_raw), "started": _epoch(now),
                 "source": source, "channel": channel, "referrer": referrer,
                 "entry": request.path, "entry_title": PAGES[request.endpoint][0]}
    title, important, feature = PAGES[request.endpoint]
    data = {"page": secrets.token_hex(16), "visitor": _digest(visitor_raw), "visit": visit,
            "path": request.path, "title": title, "important": important, "feature": feature,
            "created": _epoch(now)}
    g.analytics = {"ticket": _signer("page").dumps(data), "visitor_cookie": _signer("visitor").dumps(visitor_raw),
                   "visit_cookie": _signer("visit").dumps(visit)}


def _set_cookies(response):
    context = getattr(g, "analytics", None)
    if context and response.status_code == 200 and response.mimetype == "text/html":
        options = dict(httponly=True, secure=current_app.config.get("SESSION_COOKIE_SECURE", False), samesite="Lax")
        response.set_cookie(VISITOR_COOKIE, context["visitor_cookie"], max_age=COOKIE_AGE, **options)
        response.set_cookie(VISIT_COOKIE, context["visit_cookie"], max_age=current_app.config["ANALYTICS_SESSION_SECONDS"], **options)
    return response


def read_ticket(value):
    if not isinstance(value, str) or len(value) > 4000:
        return None
    try:
        data = _signer("page").loads(value, max_age=86400)
        visitor = _read_cookie(VISITOR_COOKIE, "visitor", COOKIE_AGE)
        if not isinstance(data, dict) or not isinstance(visitor, str) or not secrets.compare_digest(data.get("visitor", ""), _digest(visitor)):
            return None
        return data
    except (BadSignature, TypeError):
        return None


def _ensure_page(store, data, now):
    page = store.get(AnalyticsPageView, data["page"])
    if page:
        return page
    visitor_id, visit_id = data["visitor"], _digest(data["visit"]["id"])
    created = datetime.fromtimestamp(data["created"], timezone.utc).replace(tzinfo=None)
    visitor = store.get(AnalyticsVisitor, visitor_id)
    returning = visitor is not None
    if visitor is None:
        store.add(AnalyticsVisitor(id=visitor_id, first_seen=created, last_seen=now))
        store.flush()
    visit = store.scalar(select(AnalyticsVisit).where(AnalyticsVisit.id == visit_id).with_for_update())
    if visit is None:
        entry = data["visit"]
        visit = AnalyticsVisit(id=visit_id, visitor_id=visitor_id, started_at=datetime.fromtimestamp(entry["started"], timezone.utc).replace(tzinfo=None),
                               last_seen=now, is_returning=returning, source=entry["source"], channel=entry["channel"],
                               referrer=entry["referrer"], entry_path=entry["entry"], entry_title=entry["entry_title"], attribution_page=entry["entry"])
        store.add(visit)
        store.flush()
    page = AnalyticsPageView(id=data["page"], visit_id=visit_id, visitor_id=visitor_id, path=data["path"], title=data["title"],
                             created_at=created, local_day=local_day(created), important=data["important"], active_seconds=0, timing_received=False)
    store.add(page)
    store.flush()
    # A delayed unload beacon must never turn an earlier page into the session's exit.
    last = store.get(AnalyticsPageView, visit.last_page_id) if visit.last_page_id else None
    if last is None or (page.created_at, page.id) > (last.created_at, last.id):
        if last and last.path == "/signup" and page.path != "/signup":
            started = store.scalar(select(AnalyticsEvent.id).where(AnalyticsEvent.visit_id == visit_id, AnalyticsEvent.name == "signup_start").limit(1))
            completed = store.scalar(select(AnalyticsEvent.id).where(AnalyticsEvent.visit_id == visit_id, AnalyticsEvent.name == "signup_complete").limit(1))
            if started and not completed:
                _event(store, last, "signup_leave", "signup_form", now, "left-signup:" + last.id)
        visit.last_page_id = page.id
        if page.path not in {"/signup", "/login"}:
            visit.attribution_page = page.path
    if data["feature"]:
        _event(store, page, "feature_use", data["feature"], now, "feature:" + page.id)
    if page.path == "/search":
        _event(store, page, "search", "library_search", now, "search:" + page.id)
    return page


def _event(store, page, name, label, now, event_id):
    if name == "signup_start":
        event_id = "signup-start:" + page.visit_id
    elif name == "signup_leave":
        event_id = "signup-leave:" + page.id
    event_id = _digest(event_id)
    if store.get(AnalyticsEvent, event_id):
        return
    visit = store.get(AnalyticsVisit, page.visit_id)
    store.add(AnalyticsEvent(id=event_id, visit_id=page.visit_id, visitor_id=page.visitor_id, page_id=page.id,
                             name=name, label=label, created_at=now, local_day=local_day(now), attribution_page=visit.attribution_page))


def collect(data, payload):
    """Idempotent cumulative timing and bounded event batches; fail open for the website."""
    for attempt in range(2):
        try:
            now = now_utc()
            with Session(db.engine) as store, store.begin():
                if payload["occurrence"]:
                    data = {**data, "page": _digest(data["page"] + ":" + payload["occurrence"])[:32], "created": _epoch(now)}
                    payload = {**payload, "occurrence": ""}
                page = _ensure_page(store, data, now)
                store.scalar(select(AnalyticsVisit.id).where(AnalyticsVisit.id == page.visit_id).with_for_update())
                seconds = min(payload["seconds"], max(0, int((now - page.created_at).total_seconds())), 14400)
                store.execute(update(AnalyticsPageView).where(AnalyticsPageView.id == page.id, AnalyticsPageView.active_seconds < seconds)
                              .values(active_seconds=seconds))
                values = {"timing_received": True, "state_sequence": payload["sequence"]}
                if payload["state"] == "ended":
                    values["ended_at"] = now
                elif payload["state"] == "active":
                    values["ended_at"] = None
                store.execute(update(AnalyticsPageView).where(AnalyticsPageView.id == page.id,
                              AnalyticsPageView.state_sequence < payload["sequence"]).values(**values))
                store.execute(update(AnalyticsVisitor).where(AnalyticsVisitor.id == page.visitor_id).values(last_seen=now))
                store.execute(update(AnalyticsVisit).where(AnalyticsVisit.id == page.visit_id).values(last_seen=now))
                for item in payload["events"]:
                    # Signup abandonment is a candidate; reports remove it after a confirmed completion.
                    if item["name"] in {"signup_start", "signup_leave"} and page.path != "/signup":
                        continue
                    _event(store, page, item["name"], item["label"], now, page.id + ":" + item["id"])
            return True
        except IntegrityError:
            if attempt:
                current_app.logger.warning("Analytics write unavailable")
        except SQLAlchemyError:
            current_app.logger.warning("Analytics write unavailable")
            return False
    return False


def record_auth_event(name, ticket=""):
    """Only successful server-side authentication can record signup/login completion."""
    if name not in {"signup_complete", "login"} or not tracking_allowed():
        return
    data = read_ticket(ticket)
    event_id = "server:" + secrets.token_hex(16)
    for attempt in range(2):
        try:
            with Session(db.engine) as store, store.begin():
                now = now_utc()
                if data:
                    page = _ensure_page(store, data, now)
                else:
                    cookie = _read_cookie(VISIT_COOKIE, "visit", current_app.config["ANALYTICS_SESSION_SECONDS"])
                    raw = _read_cookie(VISITOR_COOKIE, "visitor", COOKIE_AGE)
                    if not isinstance(cookie, dict) or not isinstance(raw, str) or cookie.get("visitor") != _digest(raw):
                        return
                    page = store.scalar(select(AnalyticsPageView).where(AnalyticsPageView.visit_id == _digest(cookie["id"]))
                                        .order_by(AnalyticsPageView.created_at.desc(), AnalyticsPageView.id.desc()).limit(1))
                    if page is None:
                        return
                if name == "signup_complete":
                    store.scalar(select(AnalyticsVisit.id).where(AnalyticsVisit.id == page.visit_id).with_for_update())
                    _event(store, page, "signup_start", "signup_form", now, "server-start:" + page.visit_id)
                _event(store, page, name, name, now, event_id)
            return
        except IntegrityError:
            if attempt:
                current_app.logger.warning("Analytics authentication event unavailable")
        except SQLAlchemyError:
            current_app.logger.warning("Analytics authentication event unavailable")
            return


def validate_payload(payload):
    if not isinstance(payload, dict) or set(payload) - {"ticket", "seconds", "state", "events", "sequence", "occurrence"}:
        return None
    seconds, state, events = payload.get("seconds", 0), payload.get("state", "active"), payload.get("events", [])
    sequence = payload.get("sequence", 0)
    occurrence = payload.get("occurrence", "")
    if not isinstance(occurrence, str) or (occurrence and not re.fullmatch(r"[a-f0-9]{16}", occurrence)):
        return None
    if (type(seconds) is not int or not 0 <= seconds <= 14400 or not isinstance(state, str)
            or state not in {"active", "hidden", "ended"} or type(sequence) is not int or not 0 <= sequence <= 100000):
        return None
    if not isinstance(events, list) or len(events) > 12:
        return None
    for event in events:
        if (not isinstance(event, dict) or set(event) != {"id", "name", "label"}
                or not isinstance(event["id"], str) or not re.fullmatch(r"[a-f0-9]{16,32}", event["id"])
                or not isinstance(event["name"], str) or not isinstance(event["label"], str)
                or event["name"] not in CLIENT_EVENTS or event["label"] not in LABELS):
            return None
    return {"seconds": seconds, "state": state, "events": events, "sequence": sequence, "occurrence": occurrence}


def refresh_visit_cookie(response, data):
    visit = _read_cookie(VISIT_COOKIE, "visit", current_app.config["ANALYTICS_SESSION_SECONDS"])
    if isinstance(visit, dict) and visit.get("id") == data["visit"]["id"]:
        response.set_cookie(VISIT_COOKIE, _signer("visit").dumps(visit), max_age=current_app.config["ANALYTICS_SESSION_SECONDS"],
                            httponly=True, secure=current_app.config.get("SESSION_COOKIE_SECURE", False), samesite="Lax")
    return response


def protect_postgres_tables(connection):
    """Keep anonymous analytics and the admin/auth authority out of Supabase's public API."""
    if connection.dialect.name == "postgresql":
        from sqlalchemy import text

        from tzstudies.models import AuthToken, LoginSession, User
        roles = ["PUBLIC", *connection.execute(text("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')")).scalars()]
        tables = (AnalyticsVisitor.__table__, AnalyticsVisit.__table__, AnalyticsPageView.__table__, AnalyticsEvent.__table__,
                  User.__table__, AuthToken.__table__, LoginSession.__table__)
        for table in tables:
            connection.execute(text(f'ALTER TABLE "{table.name}" ENABLE ROW LEVEL SECURITY'))
            for role in roles:
                # Only fixed client roles returned by the allowlisted query are used here.
                if role in {"PUBLIC", "anon", "authenticated"}:
                    connection.execute(text(f'REVOKE ALL ON TABLE "{table.name}" FROM {role}'))


def init_analytics(app):
    app.before_request(_prepare_page)
    app.after_request(_set_cookies)

    @before_render_template.connect_via(app)
    def exclude_error_pages(sender, template, context, **extra):
        if template.name and template.name.startswith("errors/"):
            g.analytics = None

    @app.cli.command("analytics-prune")
    @click.option("--days", type=click.IntRange(min=30), default=365, show_default=True)
    def prune(days):
        """Delete anonymous analytics older than DAYS; keep user accounts untouched."""
        cutoff = now_utc() - timedelta(days=days)
        with Session(db.engine) as store, store.begin():
            store.execute(delete(AnalyticsEvent).where(AnalyticsEvent.created_at < cutoff))
            # Whole sessions are removed together to preserve foreign-key and journey integrity.
            old_visits = select(AnalyticsVisit.id).where(AnalyticsVisit.last_seen < cutoff)
            store.execute(delete(AnalyticsEvent).where(AnalyticsEvent.visit_id.in_(old_visits)))
            store.execute(delete(AnalyticsPageView).where(AnalyticsPageView.visit_id.in_(old_visits)))
            store.execute(delete(AnalyticsVisit).where(AnalyticsVisit.last_seen < cutoff))
            store.execute(delete(AnalyticsVisitor).where(AnalyticsVisitor.last_seen < cutoff,
                          ~exists().where(AnalyticsVisit.visitor_id == AnalyticsVisitor.id)))
        click.echo("Old anonymous analytics removed. User accounts were not changed.")


def parse_collect_request():
    if request.content_length and request.content_length > 12000:
        return None
    if request.is_json:
        return request.get_json(silent=True)
    try:
        raw = request.form.get("payload", "")
        return json.loads(raw) if len(raw) <= 10000 else None
    except (ValueError, TypeError):
        return None
