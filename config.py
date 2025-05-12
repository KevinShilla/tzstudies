import os

class Config:
    raw_db_url = os.getenv("DATABASE_URL")           # set on Render
    fixed_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = fixed_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
