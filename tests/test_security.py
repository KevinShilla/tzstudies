"""Security boundaries, with adversarial requests and CSRF enabled where relevant."""
import importlib.util
import re
import ssl
import time
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from pypdf import PdfWriter
from pypdf.actions import JavaScript
from redis.exceptions import RedisError
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import MultiDict
from werkzeug.security import check_password_hash

from tzstudies import create_app
from tzstudies.config import ProductionConfig
from tzstudies.extensions import db, mail
from tzstudies.models import AuthToken, Comment, LoginSession, Paper, TutorApplication, User
from tzstudies.routes.auth import _generate_token
from tzstudies.security import token_digest

PASSPHRASE = "orbit mango river lantern"


def csrf(client, path="/login"):
    page = client.get(path)
    return re.search(rb'name="csrf-token" content="([^"]+)"', page.data).group(1).decode()


def reset_token(app):
    with app.app_context():
        return _generate_token(User.query.filter_by(email="test@example.com").one(), "password-reset")


def pdf_bytes(script=False):
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    if script:
        writer.add_open_action(JavaScript("app.alert('untrusted');"))
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def tutor_data():
    return dict(name="Applicant", location="Arusha", school="School", hourly_rate="10000",
                experience="3 years", classes_taught="Form 2", email="applicant@example.com", profile_bio="Tutor profile")


def test_csp_and_sensitive_cache_headers(client):
    first, second = client.get("/"), client.get("/")
    for response in (first, second):
        csp = response.headers["Content-Security-Policy"]
        assert "script-src-attr 'none'" in csp
        assert "object-src 'none'" in csp
        assert "'unsafe-inline'" not in csp.split("script-src ")[1].split(";")[0]
        nonce = re.search(r"'nonce-([^']+)'", csp).group(1)
        assert f'<script nonce="{nonce}">'.encode() in response.data
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
        assert response.headers["Referrer-Policy"] == "same-origin"
        assert "no-store" in response.headers["Cache-Control"]
    assert first.headers["Content-Security-Policy"] != second.headers["Content-Security-Policy"]


@pytest.mark.parametrize("path", ["/signup", "/login", "/forgot-password", "/become_tutor", "/upload_exams", "/logout", "/resend-verification", "/ask"])
def test_missing_csrf_rejected(client, app, monkeypatch, path):
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)
    response = client.post(path, json={"query": "question"}) if path == "/ask" else client.post(path, data={})
    assert response.status_code == 400
    assert b"Traceback" not in response.data
    if path == "/ask":
        assert response.is_json


def test_valid_csrf_forms_and_json_work(client, app, monkeypatch):
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", True)
    token = csrf(client)
    assert client.post("/ask", json={"query": ""}, headers={"X-CSRFToken": token}).get_json()["error"] == "No query provided."
    response = client.post("/signup", data={"name": "New", "email": "csrf@example.com", "password": PASSPHRASE, "csrf_token": token})
    assert response.status_code == 302
    assert b"Hello, New" in client.get("/").data
    # Login rotates the session and CSRF secret; the old form token is rejected.
    assert client.post("/logout", data={"csrf_token": token}).status_code == 400
    assert client.post("/logout", data={"csrf_token": csrf(client, "/")}).status_code == 302


@pytest.mark.parametrize("path", ["/logout", "/resend-verification"])
def test_state_changes_cannot_use_get(auth_client, path):
    assert auth_client.get(path).status_code == 405
    assert auth_client.get("/history").status_code == 200


@pytest.mark.parametrize("password", ["short123", "a" * 15, "password123456789", "x" * 129])
def test_weak_and_oversized_passwords_rejected(client, app, password):
    client.post("/signup", data={"name": "Name", "email": "weak@example.com", "password": password})
    with app.app_context():
        assert User.query.count() == 0


def test_password_hash_and_signup_role_are_server_controlled(client, app):
    client.post("/signup", data={"name": "Student", "email": "student@example.com", "password": PASSPHRASE, "is_admin": "true", "email_verified": "true"})
    with app.app_context():
        user = User.query.one()
        assert not user.is_admin and not user.email_verified
        assert user.pw_hash.startswith("scrypt:32768:8:3$")
        assert check_password_hash(user.pw_hash, PASSPHRASE)
        assert PASSPHRASE not in user.pw_hash
    assert client.get("/admin/api/stats").status_code == 403


@pytest.mark.parametrize("email", ["bad\r\nBcc: victim@example.com", "no-at", "x@bad..com", ".x@example.com", "x@-bad.com"])
def test_bad_email_inputs_rejected(client, app, email):
    client.post("/signup", data={"name": "Name", "email": email, "password": PASSPHRASE})
    with app.app_context():
        assert User.query.count() == 0


def test_sql_injection_does_not_authenticate(client, sample_user, app):
    response = client.post("/login", data={"email": "' OR 1=1;--", "password": "password123"})
    assert b"Invalid email or password" in response.data
    assert client.get("/admin/api/stats").status_code == 302
    with app.app_context():
        assert User.query.count() == 1
        assert LoginSession.query.count() == 0


def test_duplicate_fields_are_rejected(client):
    response = client.post("/signup", data=MultiDict([("email", "first@example.com"), ("email", "second@example.com")]))
    assert response.status_code == 400


def test_request_body_is_bounded(client):
    assert client.post("/ask", data=b"x" * (65 * 1024), content_type="application/json").status_code == 413


@pytest.mark.parametrize("target", ["/%2Fexample.com", "/%5Cexample.com", "/%0Aevil", "/" + "x" * 2001])
def test_encoded_redirects_rejected(client, sample_user, target):
    response = client.post("/login", query_string={"next": target}, data={"email": "test@example.com", "password": "password123"})
    assert response.location == "/"


def test_reset_is_single_use_and_revokes_all_sessions(app, client, auth_client):
    other = app.test_client()
    other.post("/login", data={"email": "test@example.com", "password": "password123"})
    token = reset_token(app)
    with app.app_context():
        row = AuthToken.query.one()
        assert row.token_hash == token_digest(token)
        assert row.token_hash != token
    response = client.post("/reset-password/" + token, data={"password": PASSPHRASE})
    assert response.status_code == 302 and response.location == "/login"
    assert auth_client.get("/history").status_code == 302
    assert other.get("/history").status_code == 302
    assert client.post("/reset-password/" + token, data={"password": "a different valid passphrase"}).location == "/forgot-password"
    with app.app_context():
        assert AuthToken.query.count() == 0 and LoginSession.query.count() == 0
        assert check_password_hash(User.query.one().pw_hash, PASSPHRASE)
    assert b"Invalid" in client.post("/login", data={"email": "test@example.com", "password": "password123"}).data
    assert client.post("/login", data={"email": "test@example.com", "password": PASSPHRASE}).location == "/"


def test_expired_and_wrong_purpose_tokens_rejected(app, client, sample_user):
    token = reset_token(app)
    assert client.get("/verify/" + token).status_code == 302
    with app.app_context():
        row = AuthToken.query.one()
        row.expires_at = int(time.time()) - 1
        db.session.commit()
    assert client.get("/reset-password/" + token).location == "/forgot-password"


def test_latest_reset_link_replaces_older_link(app, client, sample_user):
    first, second = reset_token(app), reset_token(app)
    assert first != second
    assert client.get("/reset-password/" + first).location == "/forgot-password"
    assert client.get("/reset-password/" + second).status_code == 200


def test_email_verification_is_single_use(app, client, sample_user):
    with app.app_context():
        token = _generate_token(User.query.one(), "email-verify")
    first = client.get("/verify/" + token, follow_redirects=True)
    assert b"Email verified!" in first.data
    with app.app_context():
        assert User.query.one().email_verified
        assert AuthToken.query.count() == 0
    assert b"Invalid or expired verification link" in client.get("/verify/" + token, follow_redirects=True).data


def test_reset_token_consumption_is_conditional(app, sample_user):
    from tzstudies.routes.auth import _consume_token
    token = reset_token(app)
    with app.app_context():
        assert _consume_token(token, "password-reset")
        assert not _consume_token(token, "password-reset")
        db.session.commit()


def test_logout_revokes_replayed_cookie(auth_client, app):
    copied = auth_client.get_cookie("session").value
    auth_client.post("/logout")
    replay = app.test_client()
    replay.set_cookie("session", copied)
    assert replay.get("/history").status_code == 302


def test_session_expiry_enforced(auth_client, app):
    with app.app_context():
        LoginSession.query.one().expires_at = int(time.time()) - 1
        db.session.commit()
    assert auth_client.get("/history").status_code == 302


def test_malformed_session_user_id_is_safe(client):
    with client.session_transaction() as session:
        session["_user_id"] = "9" * 10000
        session["login_token"] = "token"
    assert client.get("/history").status_code == 302


@pytest.mark.parametrize("path", ["/serve/../README.md", "/serve/solutions/English-F2-2024.json", "/serve/../answer_keys/English-F2-2024-AnswerKey.pdf", "/serve_key/README.md", "/download/..%5CREADME.md"])
def test_only_catalogue_pdfs_can_be_served(auth_client, path):
    assert auth_client.get(path).status_code == 404


def test_pdf_symlink_cannot_escape_catalogue(client, tmp_path, monkeypatch):
    from tzstudies.routes import papers
    root = tmp_path / "exams"
    root.mkdir()
    outside = tmp_path / "private.pdf"
    outside.write_bytes(pdf_bytes())
    try:
        (root / "leak.pdf").symlink_to(outside)
    except OSError:
        pytest.skip("Symlink creation unavailable on this host")
    monkeypatch.setattr(papers, "_get_exams_folder", lambda: str(root))
    assert client.get("/serve/leak.pdf").status_code == 404


def test_script_pdf_and_fake_cv_rejected(client, app, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "CV_STORAGE_FOLDER", str(tmp_path))
    for body in (b"<html><script>alert(1)</script></html>", pdf_bytes(script=True)):
        response = client.post("/become_tutor", data={**tutor_data(), "cv_file": (BytesIO(body), "cv.pdf")})
        assert response.status_code == 302
    with app.app_context():
        assert TutorApplication.query.count() == 0
    assert not list(tmp_path.iterdir())


def test_cv_private_random_filename_and_admin_authorization(auth_client, app, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "CV_STORAGE_FOLDER", str(tmp_path))
    response = auth_client.post("/become_tutor", data={**tutor_data(), "cv_file": (BytesIO(pdf_bytes()), "../../private.pdf")})
    assert response.status_code == 302
    with app.app_context():
        application = TutorApplication.query.one()
        application_id = application.id
        assert re.fullmatch(r"[a-f0-9]{64}\.pdf", application.cv_filename)
        assert (tmp_path / application.cv_filename).is_file()
    assert auth_client.get(f"/admin/cv/{application_id}").status_code == 403
    assert app.test_client().get(f"/admin/cv/{application_id}").status_code == 302
    with app.app_context():
        User.query.filter_by(email="test@example.com").one().is_admin = True
        db.session.commit()
    response = auth_client.get(f"/admin/cv/{application_id}")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment")
    assert "no-store" in response.headers["Cache-Control"]


def test_cv_cleanup_after_database_failure(client, app, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "CV_STORAGE_FOLDER", str(tmp_path))
    with patch.object(db.session, "commit", side_effect=IntegrityError("statement", {}, Exception("private database details"))):
        response = client.post("/become_tutor", data={**tutor_data(), "cv_file": (BytesIO(pdf_bytes()), "cv.pdf")}, follow_redirects=True)
    assert b"try again shortly" in response.data
    assert b"private database details" not in response.data
    assert not list(tmp_path.iterdir())


def test_docx_external_relationship_rejected(client, app):
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<document/>")
        archive.writestr("word/_rels/document.xml.rels", '<Relationships><Relationship TargetMode="External" Target="https://attacker.invalid/"/></Relationships>')
    output.seek(0)
    client.post("/become_tutor", data={**tutor_data(), "cv_file": (output, "cv.docx")})
    with app.app_context():
        assert TutorApplication.query.count() == 0


def test_stored_xss_is_escaped_and_reply_id_bounded(auth_client, app):
    auth_client.get("/view/BasicMath-F2-2021.pdf")
    with app.app_context():
        paper_id = Paper.query.filter_by(category="exam").first().id
    body = '<img src=x onerror="alert(document.cookie)">'
    auth_client.post(f"/paper/{paper_id}/comment", data={"body": body})
    response = auth_client.get(f"/paper/{paper_id}")
    assert b"&lt;img" in response.data and body.encode() not in response.data
    assert auth_client.post(f"/paper/{paper_id}/comment", data={"body": "reply", "parent_id": "9" * 1000}).status_code == 400
    with app.app_context():
        assert Comment.query.count() == 1


def test_health_error_does_not_leak_database_details(client):
    with patch.object(db.session, "execute", side_effect=RuntimeError("postgresql://private:password@host/database")):
        response = client.get("/health")
    assert response.status_code == 503
    assert response.get_json() == {"status": "unhealthy"}
    assert b"password" not in response.data


def production_app(monkeypatch, hops=0):
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "ea0d677948ad7b87a6c99ea4dfe928bd4e3b2d9f0e099931e7df6b3f7684a169")
    monkeypatch.setattr(ProductionConfig, "SQLALCHEMY_DATABASE_URI", "sqlite://")
    monkeypatch.setattr(ProductionConfig, "RATELIMIT_STORAGE_URI", "redis://localhost:6379/0")
    monkeypatch.setattr(ProductionConfig, "RATELIMIT_ENABLED", False)
    monkeypatch.setattr(ProductionConfig, "TRUSTED_PROXY_HOPS", hops)
    monkeypatch.setattr(ProductionConfig, "TRUSTED_HOSTS", None)
    monkeypatch.setattr(ProductionConfig, "PUBLIC_BASE_URL", "https://mytzstudies.com")
    return create_app("production")


def test_production_https_hosts_and_cookies(monkeypatch):
    app = production_app(monkeypatch)
    client = app.test_client()
    assert client.get("/", base_url="https://attacker.invalid").status_code == 400
    assert client.get("/login", base_url="http://mytzstudies.com", headers={"X-Forwarded-Proto": "https"}).status_code == 308
    assert client.post("/login", base_url="http://mytzstudies.com").status_code == 400
    response = client.get("/login", base_url="https://mytzstudies.com")
    assert response.status_code == 200
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000"
    cookie = response.headers["Set-Cookie"]
    assert "Secure;" in cookie and "HttpOnly;" in cookie and "SameSite=Lax" in cookie
    assert app.config["DEBUG"] is False
    token = re.search(rb'name="csrf-token" content="([^"]+)"', response.data).group(1).decode()
    # Same-origin referrers must remain available for Flask-WTF's HTTPS check.
    response = client.post("/login", base_url="https://mytzstudies.com", data={"email": "unknown@example.com", "password": "wrong", "csrf_token": token}, headers={"Referer": "https://mytzstudies.com/login"})
    assert response.status_code == 200 and b"Invalid email or password" in response.data


def test_explicit_proxy_count(monkeypatch):
    app = production_app(monkeypatch, hops=1)
    response = app.test_client().get("/login", base_url="http://mytzstudies.com", headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": "attacker.invalid"})
    assert response.status_code == 200


def test_production_rejects_weak_secret_and_memory_limits(monkeypatch):
    production_app(monkeypatch)
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "dev-insecure-key-change-me")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", "ea0d677948ad7b87a6c99ea4dfe928bd4e3b2d9f0e099931e7df6b3f7684a169")
    monkeypatch.setattr(ProductionConfig, "RATELIMIT_STORAGE_URI", "memory://")
    with pytest.raises(RuntimeError, match="REDIS_URL"):
        create_app("production")


def test_smtp_verifies_tls_before_login(app):
    with app.app_context():
        with patch("tzstudies.secure_mail.smtplib.SMTP") as smtp:
            mail.connect().configure_host()
            context = smtp.return_value.starttls.call_args.kwargs["context"]
            assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
            assert smtp.call_args.kwargs["timeout"] == 15


def test_atomic_cv_creation_never_overwrites(app, tmp_path, monkeypatch):
    from tzstudies.file_security import store_cv
    monkeypatch.setitem(app.config, "CV_STORAGE_FOLDER", str(tmp_path))
    monkeypatch.setattr("tzstudies.file_security.secrets.token_hex", lambda _: "a" * 64)
    with app.app_context():
        filename = store_cv(b"original", ".pdf")
        with pytest.raises(FileExistsError):
            store_cv(b"replacement", ".pdf")
    assert (tmp_path / filename).read_bytes() == b"original"


@pytest.mark.parametrize("path", ["/paper/2147483648", "/admin/cv/99999999999999999999999999", "/paper/0"])
def test_integer_id_bounds(client, path):
    assert client.get(path).status_code == 404


def test_unavailable_rate_storage_returns_safe_503(client, app):
    def unavailable():
        raise RedisError("redis://private:secret@host")
    app.view_functions["ai.ask"] = unavailable
    try:
        response = client.post("/ask", json={"query": "question"})
        assert response.status_code == 503
        assert "temporarily unavailable" in response.get_json()["error"]
        assert b"secret" not in response.data
    finally:
        from tzstudies.routes.ai import ask
        app.view_functions["ai.ask"] = ask


def test_auth_migration_creates_tables_and_can_follow_bootstrap():
    source = Path(__file__).resolve().parents[1] / "migrations/versions/6c39d819a471_add_auth_tokens_and_sessions.py"
    spec = importlib.util.spec_from_file_location("auth_migration", source)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        User.__table__.create(connection)
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            migration.upgrade()
        inspector = inspect(connection)
        assert {"auth_token", "login_session"}.issubset(inspector.get_table_names())
        assert {"token_hash", "user_id", "purpose", "credential_hash", "expires_at"} == {column["name"] for column in inspector.get_columns("auth_token")}
        assert {"ix_login_session_user_id", "ix_login_session_expires_at"} == {index["name"] for index in inspector.get_indexes("login_session")}
