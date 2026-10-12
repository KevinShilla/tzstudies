"""Preserve existing orders while adding PayPal provider and lifecycle metadata."""

from alembic import op

from tzstudies.payment_models import protect_payment_tables, upgrade_payment_schema

revision = "c912d34f5e60"
down_revision = "bd74e902a631"
branch_labels = None
depends_on = None


def upgrade():
    upgrade_payment_schema(op.get_bind())
    protect_payment_tables(op.get_bind())


def downgrade():
    # Provider IDs and refund history must never be destroyed during rollback.
    pass
