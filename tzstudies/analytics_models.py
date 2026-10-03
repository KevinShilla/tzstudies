"""First-party analytics. No account IDs, IP addresses or form contents are stored."""

from tzstudies.extensions import db


class AnalyticsVisitor(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    first_seen = db.Column(db.DateTime, nullable=False, index=True)
    last_seen = db.Column(db.DateTime, nullable=False)


class AnalyticsVisit(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    visitor_id = db.Column(db.String(64), db.ForeignKey("analytics_visitor.id"), nullable=False, index=True)
    started_at = db.Column(db.DateTime, nullable=False, index=True)
    last_seen = db.Column(db.DateTime, nullable=False, index=True)
    is_returning = db.Column(db.Boolean, nullable=False)
    source = db.Column(db.String(120), nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    referrer = db.Column(db.String(253), nullable=False)
    entry_path = db.Column(db.String(300), nullable=False)
    entry_title = db.Column(db.String(200), nullable=False)
    last_page_id = db.Column(db.String(32))
    attribution_page = db.Column(db.String(300), nullable=False)


class AnalyticsPageView(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    visit_id = db.Column(db.String(64), db.ForeignKey("analytics_visit.id"), nullable=False, index=True)
    visitor_id = db.Column(db.String(64), db.ForeignKey("analytics_visitor.id"), nullable=False, index=True)
    path = db.Column(db.String(300), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, index=True)
    local_day = db.Column(db.Date, nullable=False, index=True)
    important = db.Column(db.Boolean, nullable=False)
    active_seconds = db.Column(db.Integer, nullable=False, default=0)
    timing_received = db.Column(db.Boolean, nullable=False, default=False)
    ended_at = db.Column(db.DateTime)
    state_sequence = db.Column(db.Integer, nullable=False, default=-1)


class AnalyticsEvent(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    visit_id = db.Column(db.String(64), db.ForeignKey("analytics_visit.id"), nullable=False, index=True)
    visitor_id = db.Column(db.String(64), db.ForeignKey("analytics_visitor.id"), nullable=False, index=True)
    page_id = db.Column(db.String(32), db.ForeignKey("analytics_page_view.id"), nullable=False, index=True)
    name = db.Column(db.String(30), nullable=False, index=True)
    label = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, index=True)
    local_day = db.Column(db.Date, nullable=False, index=True)
    attribution_page = db.Column(db.String(300), nullable=False)
