import os

class Config:
    raw_db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:67b17b31-714c-8007-8980-f01cf26e8ab1@db.zqnombmgoaattmgpnrrx.supabase.co:5432/postgres"
    )

    fixed_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = fixed_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
