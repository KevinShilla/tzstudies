"""align schema with new models

Revision ID: 0b594a9c63bf
Revises: 
Create Date: 2026-03-23 08:11:03.783237

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b594a9c63bf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    # If tables don't exist yet (fresh DB), create them all and return.
    # Flask-Migrate / db.create_all will handle initial creation.
    if "user" not in existing_tables:
        # Fresh database — nothing to alter. Tables will be created by
        # db.create_all() or a subsequent full-schema migration.
        return

    # --- user table: add missing columns ---
    user_columns = {c["name"] for c in inspector.get_columns("user")}

    if "is_admin" not in user_columns:
        op.add_column(
            "user",
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )

    if "email_verified" not in user_columns:
        op.add_column(
            "user",
            sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )

    # --- tutor_application table: rename cv_bio -> cv_filename, add created_at ---
    if "tutor_application" not in existing_tables:
        return

    tutor_columns = {c["name"] for c in inspector.get_columns("tutor_application")}

    if "cv_filename" not in tutor_columns:
        op.add_column(
            "tutor_application",
            sa.Column("cv_filename", sa.String(255), nullable=True),
        )

    if "created_at" not in tutor_columns:
        op.add_column(
            "tutor_application",
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = set(inspector.get_table_names())

    if "tutor_application" in existing_tables:
        tutor_columns = {c["name"] for c in inspector.get_columns("tutor_application")}
        if "created_at" in tutor_columns:
            op.drop_column("tutor_application", "created_at")
        if "cv_filename" in tutor_columns:
            op.drop_column("tutor_application", "cv_filename")

    if "user" in existing_tables:
        user_columns = {c["name"] for c in inspector.get_columns("user")}
        if "email_verified" in user_columns:
            op.drop_column("user", "email_verified")
        if "is_admin" in user_columns:
            op.drop_column("user", "is_admin")
