"""Shared request validation and browser protections. Never interpret user input."""
import hashlib
import re
import secrets
from urllib.parse import urlsplit

from flask import abort, g, jsonify, redirect, request
from redis.exceptions import RedisError
from werkzeug.exceptions import SecurityError, ServiceUnavailable
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

PASSWORD_METHOD = "scrypt:32768:8:3"
PASSWORD_MIN = 15
PASSWORD_MAX = 128


def token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def valid_text(value, maximum, multiline=False):
    return bool(value) and len(value) <= maximum and all(
        ord(char) >= 32 or (multiline and char in "\n\r\t") for char in value
    ) and "\x7f" not in value


def valid_email(value, maximum=120):
    if not valid_text(value, maximum) or value.count("@") != 1:
        return False
    local, domain = value.rsplit("@", 1)
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}", local):
        return False
    if local.startswith(".") or local.endswith(".") or ".." in local:
        return False
    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}", domain)) and all(
        label and len(label) <= 63 and not label.startswith("-") and not label.endswith("-")
        for label in domain.split(".")
    )


def password_error(password):
    if len(password) < PASSWORD_MIN:
        return "Use at least 15 characters. A few unrelated words make a memorable passphrase."
    if len(password) > PASSWORD_MAX:
        return "Keep your password under 129 characters."
    common = {"passwordpassword", "password123456789", "123456789012345", "qwertyuiopasdfgh", "letmeinletmeinletmein"}
    if password.casefold() in common or len(set(password)) < 4:
        return "Choose a less predictable password. Try a few unrelated words."
    return None


def hash_password(password):
    return generate_password_hash(password, method=PASSWORD_METHOD)


def account_limit_key():
    # Do not retain email addresses in the rate-limit backend.
    return "account:" + token_digest(request.form.get("email", "").strip().lower()[:255])


def configure_security(app, production=False):
    if production:
        secret = app.config["SECRET_KEY"]
        if len(secret) < 32 or len(set(secret)) < 10 or any(word in secret.lower() for word in ("change-me", "change_me", "generate-with", "insecure", "your-secret")):
            raise RuntimeError("Production requires a randomly generated SECRET_KEY of at least 32 characters.")
        base = urlsplit(app.config["PUBLIC_BASE_URL"])
        if base.scheme != "https" or not base.hostname or base.username or base.password or base.path not in ("", "/") or base.query or base.fragment:
            raise RuntimeError("PUBLIC_BASE_URL must be the canonical HTTPS website origin.")
        hosts = app.config.get("TRUSTED_HOSTS") or []
        app.config["TRUSTED_HOSTS"] = list(dict.fromkeys([base.hostname, "www." + base.hostname, *hosts]))
        if not str(app.config["RATELIMIT_STORAGE_URI"]).startswith(("redis://", "rediss://")):
            raise RuntimeError("Production requires REDIS_URL for shared, fail-closed rate limits.")
    hops = app.config.get("TRUSTED_PROXY_HOPS", 0)
    if not isinstance(hops, int) or not 0 <= hops <= 3:
        raise RuntimeError("TRUSTED_PROXY_HOPS must be between 0 and 3.")
    if hops:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=hops, x_proto=hops, x_host=0, x_port=0, x_prefix=0)

    @app.before_request
    def validate_request():
        g.csp_nonce = secrets.token_urlsafe(24)
        if any(isinstance(value, int) and name.endswith("_id") and not 1 <= value <= 2147483647 for name, value in (request.view_args or {}).items()):
            abort(404)
        if production and not request.is_secure:
            if request.path == "/health":
                return None  # Non-sensitive platform health probes may use HTTP.
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                abort(400, description="Use HTTPS to submit this form.")
            return redirect(app.config["PUBLIC_BASE_URL"].rstrip("/") + request.full_path.rstrip("?"), code=308)
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if request.endpoint not in ("upload.upload_exams", "tutors.become_tutor"):
                request.max_content_length = 64 * 1024
            if request.mimetype != "application/json":
                if any(len(request.form.getlist(key)) != 1 for key in request.form):
                    abort(400, description="Please submit each form field once.")
                if any(len(request.files.getlist(key)) != 1 for key in request.files):
                    abort(400, description="Please select one file per upload field.")

    @app.context_processor
    def security_context():
        return {"csp_nonce": getattr(g, "csp_nonce", "")}

    @app.after_request
    def security_headers(response):
        nonce = getattr(g, "csp_nonce", secrets.token_urlsafe(24))
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; script-src-attr 'none'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; "
            "connect-src 'self'; frame-src 'self'; frame-ancestors 'self'; "
            "object-src 'none'; base-uri 'none'; form-action 'self'; worker-src 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "no-referrer" if request.endpoint and request.endpoint.startswith("payments.") else "same-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        if production and request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        if response.mimetype == "text/html" or request.endpoint in ("papers.serve_key", "papers.download_key") or request.path.startswith(("/admin", "/ask")):
            response.headers["Cache-Control"] = "no-store, private"
            response.vary.add("Cookie")
        return response

    @app.errorhandler(400)
    @app.errorhandler(413)
    @app.errorhandler(503)
    def safe_error(error):
        from flask import render_template
        if isinstance(error, SecurityError):
            return "Invalid host.", 400, {"Content-Type": "text/plain; charset=utf-8"}
        messages = {
            400: "The request could not be accepted. Refresh the page and check your input.",
            413: "This upload is too large. Please choose a file under 10 MB.",
            503: "This service is temporarily unavailable. Please try again shortly.",
        }
        message = messages.get(error.code, messages[400])
        if request.is_json or request.path.startswith(("/api/", "/ask")):
            return jsonify({"error": message}), error.code
        return render_template("errors/request.html", message=message, status=error.code), error.code

    @app.errorhandler(RedisError)
    def rate_limit_backend_unavailable(error):
        app.logger.error("Request limit storage is unavailable")
        return safe_error(ServiceUnavailable())
