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

    # Configure logging
    _configure_logging(app)

    return app


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
