from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import check_password_hash, generate_password_hash

from tzstudies.extensions import db, limiter, mail
from tzstudies.models import User

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _generate_token(email, salt):
    return _get_serializer().dumps(email, salt=salt)


def _verify_token(token, salt, max_age=3600):
    """Return email or None."""
    try:
        return _get_serializer().loads(token, salt=salt, max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------

@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("papers.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")

        if not email or not name or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.signup"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("auth.signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("auth.signup"))

        user = User(
            email=email,
            name=name,
            pw_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        # Send verification email (best-effort)
        _send_verification_email(user)

        login_user(user)
        flash("Welcome to TZStudies! Check your email to verify your account.", "success")
        return redirect(url_for("papers.index"))

    return render_template("signup.html")


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("15 per hour", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("papers.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.pw_hash, password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("papers.index"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("papers.index"))


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------

def _send_verification_email(user):
    """Send a verification email to the user (best-effort)."""
    try:
        token = _generate_token(user.email, salt="email-verify")
        verify_url = url_for("auth.verify_email", token=token, _external=True)
        msg = Message(
            subject="Verify your TZStudies account",
            recipients=[user.email],
        )
        msg.body = (
            f"Hi {user.name},\n\n"
            f"Welcome to TZStudies! Please verify your email:\n\n"
            f"{verify_url}\n\n"
            f"This link expires in 1 hour.\n\n"
            f"— TZStudies Team"
        )
        mail.send(msg)
    except Exception as exc:
        current_app.logger.warning("Failed to send verification email: %s", exc)


@auth_bp.route("/verify/<token>")
def verify_email(token):
    email = _verify_token(token, salt="email-verify", max_age=3600)
    if not email:
        flash("Invalid or expired verification link.", "error")
        return redirect(url_for("papers.index"))

    user = User.query.filter_by(email=email).first()
    if user and not user.email_verified:
        user.email_verified = True
        db.session.commit()
        flash("Email verified! Thank you.", "success")
    elif user:
        flash("Email already verified.", "info")
    else:
        flash("User not found.", "error")

    return redirect(url_for("papers.index"))


@auth_bp.route("/resend-verification")
@login_required
def resend_verification():
    if current_user.email_verified:
        flash("Your email is already verified.", "info")
    else:
        _send_verification_email(current_user)
        flash("Verification email sent! Check your inbox.", "success")
    return redirect(url_for("papers.index"))


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                token = _generate_token(user.email, salt="password-reset")
                reset_url = url_for("auth.reset_password", token=token, _external=True)
                msg = Message(
                    subject="Reset your TZStudies password",
                    recipients=[user.email],
                )
                msg.body = (
                    f"Hi {user.name},\n\n"
                    f"You requested a password reset:\n\n"
                    f"{reset_url}\n\n"
                    f"This link expires in 1 hour. If you didn't request this, ignore this email.\n\n"
                    f"— TZStudies Team"
                )
                mail.send(msg)
            except Exception as exc:
                current_app.logger.warning("Failed to send reset email: %s", exc)

        # Always show same message (don't reveal if email exists)
        flash("If that email is registered, you'll receive a reset link shortly.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = _verify_token(token, salt="password-reset", max_age=3600)
    if not email:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        user = User.query.filter_by(email=email).first()
        if user:
            user.pw_hash = generate_password_hash(password)
            db.session.commit()
            flash("Password updated! You can now log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found.", "error")
            return redirect(url_for("auth.forgot_password"))

    return render_template("reset_password.html", token=token)
