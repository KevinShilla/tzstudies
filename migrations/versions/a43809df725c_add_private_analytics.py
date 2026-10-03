"""Add anonymous analytics and protect its tables from public Supabase access.

Revision ID: a43809df725c
Revises: 6c39d819a471
"""
import sqlalchemy as sa
from alembic import op

revision = "a43809df725c"
down_revision = "6c39d819a471"
branch_labels = None
depends_on = None


def upgrade():
    existing = set(sa.inspect(op.get_bind()).get_table_names())
    tables = {
        "analytics_visitor": [sa.Column("id", sa.String(64), primary_key=True),
                              sa.Column("first_seen", sa.DateTime, nullable=False), sa.Column("last_seen", sa.DateTime, nullable=False)],
        "analytics_visit": [sa.Column("id", sa.String(64), primary_key=True),
                            sa.Column("visitor_id", sa.String(64), sa.ForeignKey("analytics_visitor.id"), nullable=False),
                            sa.Column("started_at", sa.DateTime, nullable=False), sa.Column("last_seen", sa.DateTime, nullable=False),
                            sa.Column("is_returning", sa.Boolean, nullable=False), sa.Column("source", sa.String(120), nullable=False),
                            sa.Column("channel", sa.String(20), nullable=False), sa.Column("referrer", sa.String(253), nullable=False),
                            sa.Column("entry_path", sa.String(300), nullable=False), sa.Column("entry_title", sa.String(200), nullable=False),
                            sa.Column("last_page_id", sa.String(32)), sa.Column("attribution_page", sa.String(300), nullable=False)],
        "analytics_page_view": [sa.Column("id", sa.String(32), primary_key=True),
                                sa.Column("visit_id", sa.String(64), sa.ForeignKey("analytics_visit.id"), nullable=False),
                                sa.Column("visitor_id", sa.String(64), sa.ForeignKey("analytics_visitor.id"), nullable=False),
                                sa.Column("path", sa.String(300), nullable=False), sa.Column("title", sa.String(200), nullable=False),
                                sa.Column("created_at", sa.DateTime, nullable=False), sa.Column("local_day", sa.Date, nullable=False),
                                sa.Column("important", sa.Boolean, nullable=False), sa.Column("active_seconds", sa.Integer, nullable=False),
                                sa.Column("timing_received", sa.Boolean, nullable=False), sa.Column("ended_at", sa.DateTime),
                                sa.Column("state_sequence", sa.Integer, nullable=False)],
        "analytics_event": [sa.Column("id", sa.String(64), primary_key=True),
                            sa.Column("visit_id", sa.String(64), sa.ForeignKey("analytics_visit.id"), nullable=False),
                            sa.Column("visitor_id", sa.String(64), sa.ForeignKey("analytics_visitor.id"), nullable=False),
                            sa.Column("page_id", sa.String(32), sa.ForeignKey("analytics_page_view.id"), nullable=False),
                            sa.Column("name", sa.String(30), nullable=False), sa.Column("label", sa.String(60), nullable=False),
                            sa.Column("created_at", sa.DateTime, nullable=False), sa.Column("local_day", sa.Date, nullable=False),
                            sa.Column("attribution_page", sa.String(300), nullable=False)],
    }
    indexes = {
        "analytics_visitor": ["first_seen"], "analytics_visit": ["visitor_id", "started_at", "last_seen"],
        "analytics_page_view": ["visit_id", "visitor_id", "path", "created_at", "local_day"],
        "analytics_event": ["visit_id", "visitor_id", "page_id", "name", "created_at", "local_day"],
    }
    for name, columns in tables.items():
        if name not in existing:
            op.create_table(name, *columns)
            for column in indexes[name]:
                op.create_index(f"ix_{name}_{column}", name, [column])
    if op.get_bind().dialect.name == "postgresql":
        roles = ["PUBLIC", *op.get_bind().execute(sa.text("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')")).scalars()]
        for name in [*tables, "user", "auth_token", "login_session"]:
            if name not in tables and name not in existing:
                continue
            op.execute(sa.text(f'ALTER TABLE "{name}" ENABLE ROW LEVEL SECURITY'))
            for role in roles:
                if role in {"PUBLIC", "anon", "authenticated"}:
                    op.execute(sa.text(f'REVOKE ALL ON TABLE "{name}" FROM {role}'))


def downgrade():
    # Private account/auth protections intentionally survive a downgrade.
    for name in ("analytics_event", "analytics_page_view", "analytics_visit", "analytics_visitor"):
        op.drop_table(name)
