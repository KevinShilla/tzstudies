import logging
import os
import sys

from flask import Flask

from tzstudies.config import config_by_name


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

    # Initialise extensions
    _init_extensions(app)

    # Register blueprints
    _register_blueprints(app)

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
        db.create_all()
        _fix_schema(db)

    # Configure logging
    _configure_logging(app)

    return app


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
        cache, csrf, db, limiter, login_manager, mail, migrate,
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
        return db.session.get(User, int(user_id))


def _register_blueprints(app):
    from tzstudies.routes.auth import auth_bp
    from tzstudies.routes.papers import papers_bp
    from tzstudies.routes.tutors import tutors_bp
    from tzstudies.routes.ai import ai_bp
    from tzstudies.routes.upload import upload_bp
    from tzstudies.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(tutors_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(admin_bp)


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        from tzstudies.extensions import db
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template("errors/403.html"), 403

    @app.errorhandler(429)
    def rate_limited(error):
        from flask import render_template
        return render_template("errors/429.html"), 429

    # Health check endpoint (for load balancers / uptime monitors)
    @app.route("/health")
    def health_check():
        from flask import jsonify
        try:
            from tzstudies.extensions import db
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"})
        except Exception as exc:
            return jsonify({"status": "unhealthy", "error": str(exc)}), 503


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
