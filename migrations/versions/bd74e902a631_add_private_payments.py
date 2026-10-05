"""Add private ClickPesa orders and idempotent webhook receipts.

Revision ID: bd74e902a631
Revises: a43809df725c
"""
import sqlalchemy as sa
from alembic import op

revision = "bd74e902a631"
down_revision = "a43809df725c"
branch_labels = None
depends_on = None


def upgrade():
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    if "payment_order" not in existing:
        op.create_table("payment_order",
                        sa.Column("id", sa.String(32), primary_key=True),
                        sa.Column("order_reference", sa.String(40), nullable=False),
                        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False),
                        sa.Column("intent_key", sa.String(64), nullable=False, unique=True),
                        sa.Column("plan_id", sa.String(60), nullable=False),
                        sa.Column("plan_name", sa.String(100), nullable=False),
                        sa.Column("plan_snapshot", sa.JSON, nullable=False),
                        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
                        sa.Column("currency", sa.String(3), nullable=False),
                        sa.Column("status", sa.String(24), nullable=False),
                        sa.Column("provider_status", sa.String(20)),
                        sa.Column("provider_id", sa.String(160), unique=True),
                        sa.Column("payment_reference", sa.String(160), unique=True),
                        sa.Column("checkout_url", sa.Text),
                        sa.Column("created_at", sa.DateTime, nullable=False),
                        sa.Column("completed_at", sa.DateTime),
                        sa.Column("last_checked_at", sa.DateTime),
                        sa.Column("updated_at", sa.DateTime, nullable=False),
                        sa.CheckConstraint("amount > 0", name="ck_payment_positive_amount"),
                        sa.CheckConstraint("currency IN ('TZS', 'USD')", name="ck_payment_currency"))
        for column in ("order_reference", "user_id", "status"):
            op.create_index(f"ix_payment_order_{column}", "payment_order", [column], unique=column == "order_reference")
    if "payment_webhook_event" not in existing:
        op.create_table("payment_webhook_event",
                        sa.Column("id", sa.String(64), primary_key=True),
                        sa.Column("order_id", sa.String(32), sa.ForeignKey("payment_order.id"), nullable=False),
                        sa.Column("event", sa.String(30), nullable=False),
                        sa.Column("provider_id", sa.String(160), nullable=False),
                        sa.Column("received_at", sa.DateTime, nullable=False),
                        sa.Column("processed_at", sa.DateTime, nullable=False))
        op.create_index("ix_payment_webhook_event_order_id", "payment_webhook_event", ["order_id"])
    if op.get_bind().dialect.name == "postgresql":
        roles = ["PUBLIC", *op.get_bind().execute(sa.text("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')")).scalars()]
        for name in ("payment_order", "payment_webhook_event"):
            op.execute(sa.text(f'ALTER TABLE "{name}" ENABLE ROW LEVEL SECURITY'))
            for role in roles:
                if role in {"PUBLIC", "anon", "authenticated"}:
                    op.execute(sa.text(f'REVOKE ALL ON TABLE "{name}" FROM {role}'))


def downgrade():
    op.drop_table("payment_webhook_event")
    op.drop_table("payment_order")
