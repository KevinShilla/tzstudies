"""Only order metadata is retained; provider payloads and payment instruments are not."""

from datetime import datetime, timezone

from tzstudies.extensions import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PaymentOrder(db.Model):
    __tablename__ = "payment_order"
    id = db.Column(db.String(32), primary_key=True)
    order_reference = db.Column(db.String(40), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    intent_key = db.Column(db.String(64), unique=True, nullable=False)
    plan_id = db.Column(db.String(60), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    plan_snapshot = db.Column(db.JSON, nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(24), nullable=False, default="creating", index=True)
    provider_status = db.Column(db.String(20))
    provider_id = db.Column(db.String(160), unique=True)
    payment_reference = db.Column(db.String(160), unique=True)
    checkout_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    completed_at = db.Column(db.DateTime)
    last_checked_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    user = db.relationship("User")
    __table_args__ = (
        db.CheckConstraint("amount > 0", name="ck_payment_positive_amount"),
        db.CheckConstraint("currency IN ('TZS', 'USD')", name="ck_payment_currency"),
    )


class PaymentWebhookEvent(db.Model):
    __tablename__ = "payment_webhook_event"
    id = db.Column(db.String(64), primary_key=True)
    order_id = db.Column(db.String(32), db.ForeignKey("payment_order.id"), nullable=False, index=True)
    event = db.Column(db.String(30), nullable=False)
    provider_id = db.Column(db.String(160), nullable=False)
    received_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    processed_at = db.Column(db.DateTime, nullable=False, default=utcnow)


def protect_payment_tables(connection):
    """Supabase browser roles must not read or modify payment records."""
    if connection.dialect.name != "postgresql":
        return
    from sqlalchemy import text
    roles = ["PUBLIC", *connection.execute(text("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')")).scalars()]
    for table in (PaymentOrder.__table__, PaymentWebhookEvent.__table__):
        connection.execute(text(f'ALTER TABLE "{table.name}" ENABLE ROW LEVEL SECURITY'))
        for role in roles:
            if role in {"PUBLIC", "anon", "authenticated"}:
                connection.execute(text(f'REVOKE ALL ON TABLE "{table.name}" FROM {role}'))
