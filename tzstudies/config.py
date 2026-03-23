import os

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
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    """Development overrides — allows missing SECRET_KEY."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
    DEBUG = True


class TestingConfig(Config):
    """Testing overrides."""

    SECRET_KEY = "test-secret-key"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # in-memory
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "NullCache"
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Production — SECRET_KEY must be set via environment."""

    pass


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
