import secrets
import threading
import time
from urllib.parse import unquote, urlsplit

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from tzstudies.analytics import record_auth_event
from tzstudies.extensions import db, limiter, mail
from tzstudies.models import AuthToken, LoginSession, User
from tzstudies.security import (
    PASSWORD_MAX,
    PASSWORD_METHOD,
    account_limit_key,
    hash_password,
    password_error,
    token_digest,
    valid_email,
    valid_text,
)

auth_bp = Blueprint("auth", __name__)
_DUMMY_HASH = hash_password(secrets.token_urlsafe(32))


def _safe_next():
    target = request.args.get("next", "")
    try:
        decoded = unquote(target)
        parts = urlsplit(decoded)
    except ValueError:
        return url_for("papers.index")
    if len(target) <= 2000 and decoded.startswith("/") and not decoded.startswith("//") and not parts.scheme and not parts.netloc and "\\" not in decoded and all(ord(c) >= 32 and ord(c) != 127 for c in decoded):
        return target
    return url_for("papers.index")


def _start_session(user):
    raw = secrets.token_urlsafe(32)
    now = int(time.time())
    db.session.execute(delete(LoginSession).where(LoginSession.expires_at <= now))
    db.session.add(LoginSession(
        token_hash=token_digest(raw), user_id=user.id,
        expires_at=now + int(current_app.permanent_session_lifetime.total_seconds()),
    ))
    db.session.commit()
    session.clear()
    session.permanent = True
    session["login_token"] = raw
    login_user(user, remember=False)


def _generate_token(user, salt):
    raw = secrets.token_urlsafe(32)
    now = int(time.time())
    # Serialize token replacement against login, verification and password reset.
    db.session.execute(update(User).where(User.id == user.id).values(pw_hash=User.pw_hash))
    db.session.refresh(user)
    db.session.execute(delete(AuthToken).where(AuthToken.expires_at <= now))
    db.session.execute(delete(AuthToken).where(AuthToken.user_id == user.id, AuthToken.purpose == salt))
    db.session.add(AuthToken(
        token_hash=token_digest(raw), user_id=user.id, purpose=salt,
        credential_hash=token_digest(user.pw_hash), expires_at=now + 3600,
    ))
    db.session.commit()
    return raw


def _verify_token(token, salt):
    if not isinstance(token, str) or len(token) != 43:
        return None
    row = db.session.get(AuthToken, token_digest(token))
    if not row or row.purpose != salt or row.expires_at <= time.time():
        return None
    user = db.session.get(User, row.user_id)
    if not user or not secrets.compare_digest(row.credential_hash, token_digest(user.pw_hash)):
        return None
    return user


def _consume_token(token, purpose):
    result = db.session.execute(delete(AuthToken).where(
        AuthToken.token_hash == token_digest(token), AuthToken.purpose == purpose,
        AuthToken.expires_at > int(time.time()),
    ))
    return result.rowcount == 1


def _send_email(msg):
    app = current_app._get_current_object()

    def send():
        with app.app_context():
            try:
                mail.send(msg)
            except Exception:
                app.logger.warning("Account email delivery failed")

    if app.testing:
        send()
    else:
        threading.Thread(target=send, daemon=True).start()


def _send_verification_email(user):
    if not current_app.config.get("MAIL_USERNAME"):
        return
    token = _generate_token(user, "email-verify")
    link = current_app.config["PUBLIC_BASE_URL"] + url_for("auth.verify_email", token=token)
    msg = Message(subject="Verify your TZStudies account", recipients=[user.email])
    msg.body = f"Hi {user.name},\n\nVerify your TZStudies account:\n\n{link}\n\nThis link expires in 1 hour.\n\nTZStudies Team"
    _send_email(msg)


@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(_safe_next())
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        if not email or not name or not password:
            flash("All fields are required.", "error")
        elif not valid_text(name, 100) or not valid_email(email):
            flash("Please enter a valid name and email address.", "error")
        elif password_error(password):
            flash(password_error(password), "error")
        else:
            user = User(email=email, name=name, pw_hash=hash_password(password))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("We couldn't create an account with those details. Try logging in or resetting your password.", "error")
                return redirect(url_for("auth.signup", next=_safe_next()))
            _start_session(user)
            record_auth_event("signup_complete", request.form.get("analytics_ticket", ""))
            _send_verification_email(user)
            message = "Welcome to TZStudies! Your free study account is ready."
            if current_app.config.get("MAIL_USERNAME"):
                message += " Check your inbox for a verification link."
            flash(message, "success")
            return redirect(_safe_next())
        return redirect(url_for("auth.signup", next=_safe_next()))
    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("50 per hour; 10 per minute", methods=["POST"])
@limiter.limit("20 per hour", key_func=account_limit_key, methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_safe_next())
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first() if valid_email(email) else None
        if len(password) <= PASSWORD_MAX:
            stored = user.pw_hash if user else _DUMMY_HASH
            try:
                correct = check_password_hash(stored, password)
            except (ValueError, TypeError):
                correct = False
            if user and correct:
                # Hold the account write lock until the new session commits.
                upgraded = user.pw_hash if user.pw_hash.startswith(PASSWORD_METHOD + "$") else hash_password(password)
                result = db.session.execute(update(User).where(User.id == user.id, User.pw_hash == stored).values(pw_hash=upgraded))
                if result.rowcount == 1:
                    _start_session(user)
                    record_auth_event("login", request.form.get("analytics_ticket", ""))
                    return redirect(_safe_next())
                db.session.rollback()
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    token = session.get("login_token", "")
    db.session.execute(delete(LoginSession).where(LoginSession.token_hash == token_digest(token)))
    db.session.commit()
    logout_user()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("papers.index"))


@auth_bp.route("/verify/<token>")
@limiter.limit("20 per hour")
def verify_email(token):
    user = _verify_token(token, "email-verify")
    if user:
        db.session.execute(update(User).where(User.id == user.id).values(email_verified=True))
        if _consume_token(token, "email-verify"):
            db.session.commit()
            flash("Email verified! Thank you.", "success")
            return redirect(url_for("papers.index"))
    db.session.rollback()
    flash("Invalid or expired verification link.", "error")
    return redirect(url_for("papers.index"))


@auth_bp.route("/resend-verification", methods=["POST"])
@login_required
@limiter.limit("3 per hour")
def resend_verification():
    if current_user.email_verified:
        flash("Your email is already verified.", "info")
    else:
        _send_verification_email(current_user)
        flash("If email is available, check your inbox for a verification link.", "info")
    return redirect(url_for("papers.index"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
@limiter.limit("3 per hour", key_func=account_limit_key, methods=["POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first() if valid_email(email) else None
        if user and current_app.config.get("MAIL_USERNAME"):
            token = _generate_token(user, "password-reset")
            link = current_app.config["PUBLIC_BASE_URL"] + url_for("auth.reset_password", token=token)
            msg = Message(subject="Reset your TZStudies password", recipients=[user.email])
            msg.body = f"Hi {user.name},\n\nReset your password:\n\n{link}\n\nThis link expires in 1 hour and works once. If you didn't request it, ignore this email.\n\nTZStudies Team"
            _send_email(msg)
        flash("If that email is registered, you'll receive a reset link shortly.", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
@limiter.limit("20 per hour")
def reset_password(token):
    user = _verify_token(token, "password-reset")
    if not user:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        error = password_error(password)
        if error:
            flash(error, "error")
            return redirect(url_for("auth.reset_password", token=token))
        old_hash, user_id = user.pw_hash, user.id
        new_hash = hash_password(password)
        changed = db.session.execute(update(User).where(User.id == user_id, User.pw_hash == old_hash).values(pw_hash=new_hash))
        if changed.rowcount != 1 or not _consume_token(token, "password-reset"):
            db.session.rollback()
            flash("Invalid or expired reset link.", "error")
            return redirect(url_for("auth.forgot_password"))
        db.session.execute(delete(LoginSession).where(LoginSession.user_id == user_id))
        db.session.execute(delete(AuthToken).where(AuthToken.user_id == user_id))
        db.session.commit()
        session.clear()
        flash("Password updated! Your previous sessions have been signed out. You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", token=token)
