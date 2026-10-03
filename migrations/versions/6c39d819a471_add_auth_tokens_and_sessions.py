"""Add revocable browser sessions and one-use account tokens.

Revision ID: 6c39d819a471
Revises: de8eb5308645
"""
import sqlalchemy as sa
from alembic import op

revision = "6c39d819a471"
down_revision = "de8eb5308645"
branch_labels = None
depends_on = None


def upgrade():
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    # The app's compatibility bootstrap may already have created these new tables.
    if "login_session" not in existing:
        op.create_table(
            "login_session", sa.Column("token_hash", sa.String(64), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
            sa.Column("expires_at", sa.BigInteger(), nullable=False),
        )
        op.create_index("ix_login_session_user_id", "login_session", ["user_id"])
        op.create_index("ix_login_session_expires_at", "login_session", ["expires_at"])
    if "auth_token" not in existing:
        op.create_table(
            "auth_token", sa.Column("token_hash", sa.String(64), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
            sa.Column("purpose", sa.String(20), nullable=False),
            sa.Column("credential_hash", sa.String(64), nullable=False),
            sa.Column("expires_at", sa.BigInteger(), nullable=False),
        )
        op.create_index("ix_auth_token_user_id", "auth_token", ["user_id"])
        op.create_index("ix_auth_token_expires_at", "auth_token", ["expires_at"])


def downgrade():
    op.drop_table("auth_token")
    op.drop_table("login_session")
