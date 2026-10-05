import logging
import os
import sys

from flask import Flask

from tzstudies.config import config_by_name
from tzstudies.security import configure_security


def create_app(config_name=None):
    """Application factory for TZStudies."""

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder=os.path.join(os.pardir, "templates"),
        static_folder=os.path.join(os.pardir, "static"),
    )

    # Load config
    cfg = config_by_name.get(config_name)
    if cfg is None:
        raise ValueError(f"Unknown config: {config_name}")
    app.config.from_object(cfg)
    # Timestamp columns and analytics boundaries use UTC, even on a database host in another timezone.
    from sqlalchemy.engine import make_url
    database_url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    if database_url.get_backend_name() == "postgresql":
        engine_options = dict(app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {}))
        connect_args = dict(engine_options.get("connect_args", {}))
        prior_options = connect_args.get("options", database_url.query.get("options", ""))
        connect_args["options"] = (prior_options + " -c timezone=UTC").strip()
        engine_options["connect_args"] = connect_args
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options
    configure_security(app, production=config_name == "production")
    from tzstudies.payment_config import configure_payments
    configure_payments(app, production=config_name == "production")

    @app.context_processor
    def shared_context():
        from datetime import datetime
        return {"current_year": datetime.now().year}

    # Initialise extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)
    from tzstudies.payments import init_payments
    init_payments(app)
    from tzstudies.routes.payments import register_payment_callbacks
    register_payment_callbacks(app)

    from tzstudies.analytics import init_analytics
    init_analytics(app)

    # Register error handlers
    _register_error_handlers(app)

    # Ensure upload directories exist
    os.makedirs(
        os.path.join(app.root_path, os.pardir, "uploads", "cvs"),
        exist_ok=True,
    )

    # Ensure tables exist and schema is up-to-date
    with app.app_context():
        from tzstudies.extensions import db
        _initialise_database(app, db)

    # Configure logging
    _configure_logging(app)

    return app


def _initialise_database(app, db):
    """Serialize compatibility bootstrap across application workers."""
    from pathlib import Path

    from filelock import FileLock
    from sqlalchemy import text

    instance = Path(app.instance_path)
    instance.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not app.debug and not app.testing and os.name != "nt":
        instance.chmod(0o700)
        (Path(app.root_path).parent / "uploads" / "cvs").chmod(0o700)

    def initialise():
        db.create_all()
        _fix_schema(db)
        from tzstudies.analytics import protect_postgres_tables
        from tzstudies.payment_models import protect_payment_tables
        with db.engine.begin() as analytics_connection:
            protect_postgres_tables(analytics_connection)
            protect_payment_tables(analytics_connection)

    if db.engine.dialect.name == "postgresql":
        with db.engine.begin() as connection:
            connection.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": 1987253301})
            initialise()
    elif db.engine.dialect.name == "sqlite" and db.engine.url.database not in (None, "", ":memory:"):
        with FileLock(str(instance / "schema.lock"), timeout=30):
            initialise()
            if os.name != "nt":
                Path(db.engine.url.database).chmod(0o600)
    else:
        initialise()


def _fix_schema(db):
    """Add any columns that exist in the models but are missing from the
    database.  This handles the case where the app was restructured and
    new columns were added to the models but the production database
    still has the old schema.  ``db.create_all()`` only creates *new*
    tables — it never alters existing ones."""

    import sqlalchemy as sa

    conn = db.engine.connect()
    inspector = sa.inspect(db.engine)
    existing_tables = set(inspector.get_table_names())

    # ── user table ────────────────────────────────────────────────
    if "user" in existing_tables:
        user_cols = {c["name"] for c in inspector.get_columns("user")}

        if "is_admin" not in user_cols:
            conn.execute(sa.text(
                "ALTER TABLE \"user\" ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"
            ))

        if "email_verified" not in user_cols:
            conn.execute(sa.text(
                "ALTER TABLE \"user\" ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE"
            ))

    # ── tutor_application table ───────────────────────────────────
    if "tutor_application" in existing_tables:
        tutor_cols = {c["name"] for c in inspector.get_columns("tutor_application")}

        if "cv_filename" not in tutor_cols:
            conn.execute(sa.text(
                "ALTER TABLE tutor_application ADD COLUMN cv_filename VARCHAR(255)"
            ))

        if "created_at" not in tutor_cols:
            conn.execute(sa.text(
                "ALTER TABLE tutor_application ADD COLUMN created_at TIMESTAMP"
            ))

        # The old schema had cv_bio (NOT NULL) which the new code doesn't
        # use. Drop it so inserts don't fail.
        if "cv_bio" in tutor_cols:
            try:
                conn.execute(sa.text(
                    "ALTER TABLE tutor_application DROP COLUMN cv_bio"
                ))
            except Exception:
                # SQLite < 3.35 doesn't support DROP COLUMN;
                # fall back to making it nullable on PostgreSQL
                try:
                    conn.execute(sa.text(
                        "ALTER TABLE tutor_application "
                        "ALTER COLUMN cv_bio DROP NOT NULL"
                    ))
                except Exception:
                    pass  # best-effort

    conn.commit()
    conn.close()


def _init_extensions(app):
    from tzstudies.extensions import (
        cache,
        csrf,
        db,
        limiter,
        login_manager,
        mail,
        migrate,
    )
    from tzstudies.models import User

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    if app.config.get("RATELIMIT_ENABLED", True):
        limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        import time

        from flask import session

        from tzstudies.models import LoginSession
        from tzstudies.security import token_digest

        if not str(user_id).isascii() or not str(user_id).isdigit() or len(str(user_id)) > 18:
            return None
        token = session.get("login_token")
        if not isinstance(token, str) or len(token) > 128:
            return None
        browser_session = db.session.get(LoginSession, token_digest(token))
        if not browser_session or browser_session.user_id != int(user_id) or browser_session.expires_at <= time.time():
            return None
        return db.session.get(User, int(user_id))


def _register_blueprints(app):
    from tzstudies.routes.admin import admin_bp
    from tzstudies.routes.ai import ai_bp
    from tzstudies.routes.analytics import analytics_bp
    from tzstudies.routes.auth import auth_bp
    from tzstudies.routes.papers import papers_bp
    from tzstudies.routes.payments import payments_bp
    from tzstudies.routes.tutors import tutors_bp
    from tzstudies.routes.upload import upload_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(tutors_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(payments_bp)


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import jsonify, render_template, request

        from tzstudies.extensions import db
        db.session.rollback()
        if request.is_json or request.path.startswith(("/api/", "/ask")):
            return jsonify({"error": "Something went wrong. Please try again shortly."}), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template("errors/403.html"), 403

    @app.errorhandler(429)
    def rate_limited(error):
        from flask import jsonify, render_template, request
        if request.is_json or request.path.startswith(("/api/", "/ask")):
            return jsonify({"error": "Too many requests. Please wait before trying again."}), 429
        return render_template("errors/429.html"), 429

    # Health check endpoint (for load balancers / uptime monitors)
    @app.route("/health")
    def health_check():
        from flask import jsonify
        try:
            from tzstudies.extensions import db
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"})
        except Exception:
            db.session.rollback()
            app.logger.error("Health check failed")
            return jsonify({"status": "unhealthy"}), 503


def _configure_logging(app):
    if not app.debug and not app.testing:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("TZStudies startup")
