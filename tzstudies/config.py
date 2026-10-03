import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv

# Load .env before reading any env vars
load_dotenv()


def _get_database_url():
    """Return a SQLAlchemy-compatible database URL."""
    raw = os.getenv("DATABASE_URL")
    if not raw:
        return "sqlite:///tzstudies.db"
    return raw.replace("postgres://", "postgresql://", 1)


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.getenv("SECRET_KEY", "")
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Flask-Mail (Gmail SMTP)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_ENABLED = True

    # Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # Security
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE = 32 * 1024
    MAX_FORM_PARTS = 24
    MAX_UPLOAD_BYTES = 10 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_REFRESH_EACH_REQUEST = False
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://mytzstudies.com").rstrip("/")
    TRUSTED_PROXY_HOPS = int(os.getenv("TRUSTED_PROXY_HOPS", "0"))
    TRUSTED_HOSTS = [host.strip() for host in (os.getenv("TRUSTED_HOSTS", "") + "," + os.getenv("RENDER_EXTERNAL_HOSTNAME", "")).split(",") if host.strip()] or None
    RATELIMIT_SWALLOW_ERRORS = False
    RATELIMIT_IN_MEMORY_FALLBACK_ENABLED = False
    RATELIMIT_HEADERS_ENABLED = True
    MAIL_DEBUG = False
    ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
    ANALYTICS_SESSION_SECONDS = 1800


class DevelopmentConfig(Config):
    """Development overrides — allows missing SECRET_KEY."""

    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = True
    TRUSTED_HOSTS = None


class TestingConfig(Config):
    """Testing overrides."""

    SECRET_KEY = "test-secret-key"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # in-memory
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "NullCache"
    MAIL_SUPPRESS_SEND = True
    TRUSTED_HOSTS = None


class ProductionConfig(Config):
    """Production — SECRET_KEY must be set via environment."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
