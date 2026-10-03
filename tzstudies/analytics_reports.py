"""Indexed aggregates for the private dashboard; bounded detail queries."""

from collections import Counter
from datetime import date, datetime, time, timedelta, timezone

from flask import current_app
from sqlalchemy import Date, String, and_, cast, func, or_, select, text

from tzstudies.analytics import PAGES, now_utc
from tzstudies.analytics_models import AnalyticsEvent as Event
from tzstudies.analytics_models import AnalyticsPageView as View
from tzstudies.analytics_models import AnalyticsVisit as Visit
from tzstudies.analytics_models import AnalyticsVisitor as Visitor
from tzstudies.extensions import db
from tzstudies.models import User

TZ = timezone(timedelta(hours=3), "Africa/Dar_es_Salaam")
PERIODS = {"today", "7d", "30d", "month", "all", "custom"}


def _naive(value):
    return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value


def date_range(args):
    today = now_utc().replace(tzinfo=timezone.utc).astimezone(TZ).date()
    period = args.get("period", "30d")
    if period not in PERIODS:
        raise ValueError("Choose a valid date range.")
    end = today
    if period == "today":
        start = today
    elif period in {"7d", "30d"}:
        start = today - timedelta(days=6 if period == "7d" else 29)
    elif period == "month":
        start = today.replace(day=1)
    elif period == "all":
        first_view = db.session.scalar(select(func.min(View.created_at)))
        first_user = db.session.scalar(select(func.min(User.created_at)).where(User.is_admin.is_(False)))
        earliest = min([_naive(value) for value in (first_view, first_user) if value] or [now_utc()])
        start = earliest.replace(tzinfo=timezone.utc).astimezone(TZ).date()
    else:
        try:
            start, end = date.fromisoformat(args.get("start", "")), date.fromisoformat(args.get("end", ""))
        except (ValueError, TypeError):
            raise ValueError("Enter a start and end date.") from None
        if not date(2000, 1, 1) <= start <= end <= today:
            raise ValueError("Dates must be ordered, from 2000 onward, and no later than today.")
    begin = datetime.combine(start, time.min, TZ).astimezone(timezone.utc).replace(tzinfo=None)
    finish = datetime.combine(end + timedelta(days=1), time.min, TZ).astimezone(timezone.utc).replace(tzinfo=None)
    return {"period": period, "start": start.isoformat(), "end": end.isoformat(), "begin": begin, "finish": finish,
            "days": (end - start).days + 1, "today": today.isoformat(), "compare": args.get("compare", "1") == "1" and period != "all"}


def _between(column, begin, finish):
    return and_(column >= begin, column < finish)


def _count(statement):
    return int(db.session.scalar(statement) or 0)


def _summary(begin, finish):
    scope = _between(View.created_at, begin, finish)
    counts = db.session.execute(select(func.count(View.id), func.count(func.distinct(View.visitor_id)),
                                       func.count(func.distinct(View.visit_id)), func.coalesce(func.sum(View.active_seconds), 0),
                                       func.sum(cast(View.timing_received, db.Integer))).where(scope)).one()
    converted = _count(select(func.count(func.distinct(Event.visitor_id))).where(
        _between(Event.created_at, begin, finish), Event.name == "signup_complete",
        Event.visitor_id.in_(select(View.visitor_id).where(scope))))
    engaged = (select(View.visit_id).where(scope).group_by(View.visit_id)
               .having(or_(func.count(View.id) >= 2, func.max(View.active_seconds) >= 10)).subquery())
    engaged_count = _count(select(func.count()).select_from(engaged))
    return {"views": counts[0], "visitors": counts[1], "visits": counts[2],
            "signups": _count(select(func.count(User.id)).where(User.is_admin.is_(False), _between(User.created_at, begin, finish))),
            "tracked_signups": _count(select(func.count(Event.id)).where(Event.name == "signup_complete", _between(Event.created_at, begin, finish))),
            "conversion": round(100 * converted / counts[1], 2) if counts[1] else 0,
            "average_time": round(counts[3] / counts[4], 1) if counts[4] else 0,
            "engaged_visits": engaged_count,
            "engagement_rate": round(100 * engaged_count / counts[2], 2) if counts[2] else 0}


def _change(current, previous, percentage=False):
    difference = round(current - previous, 2)
    return {"current": current, "previous": previous, "direction": "up" if difference > 0 else "down" if difference < 0 else "flat",
            "change": difference if percentage else round(100 * difference / previous, 1) if previous else None,
            "unit": "pp" if percentage else "%"}


def _user_day():
    if db.engine.dialect.name == "postgresql":
        return cast(User.created_at + text("INTERVAL '3 hours'"), Date)
    return func.date(User.created_at, "+3 hours")


def _trend(begin, finish, days, start_day, end_day):
    monthly = days > 90
    bucket = func.substr(cast(View.local_day, String), 1, 7 if monthly else 10)
    visitors = {key: (count, views) for key, count, views in db.session.execute(
        select(bucket, func.count(func.distinct(View.visitor_id)), func.count(View.id))
        .where(_between(View.created_at, begin, finish)).group_by(bucket))}
    user_bucket = func.substr(cast(_user_day(), String), 1, 7 if monthly else 10)
    signups = dict(db.session.execute(select(user_bucket, func.count(User.id)).where(
        User.is_admin.is_(False), _between(User.created_at, begin, finish)).group_by(user_bucket)).all())
    cursor, end = date.fromisoformat(start_day), date.fromisoformat(end_day)
    cursor = cursor.replace(day=1) if monthly else cursor
    points = []
    while cursor <= end:
        key = cursor.isoformat()[:7] if monthly else cursor.isoformat()
        count, views = visitors.get(key, (0, 0))
        points.append({"date": key, "visitors": count, "views": views, "signups": signups.get(key, 0)})
        cursor = ((cursor.replace(day=28) + timedelta(days=4)).replace(day=1) if monthly else cursor + timedelta(days=1))
    return {"interval": "month" if monthly else "day", "points": points}


def _known_pages():
    """Include unvisited public pages so least-visited genuinely includes zero views."""
    from flask import url_for

    from tzstudies.routes.papers import _catalogue
    pages = {}
    for endpoint, (title, _, _) in PAGES.items():
        if endpoint not in {"papers.view_exam", "papers.view_key", "papers.paper_detail"}:
            pages[url_for(endpoint)] = title
    for exam in _catalogue():
        title = f'{exam["subject"]} · {exam["level"]} · {exam["year"]}'
        pages[url_for("papers.view_exam", filename=exam["filename"])] = title
        if exam["answer_key"]:
            pages[url_for("papers.view_key", filename=exam["answer_key"])] = title + " answer key"
    return pages


def report(args):
    window = date_range(args)
    begin, finish = window["begin"], window["finish"]
    view_scope, event_scope = _between(View.created_at, begin, finish), _between(Event.created_at, begin, finish)
    summary = _summary(begin, finish)
    comparison = None
    if window["compare"]:
        previous = _summary(begin - timedelta(days=window["days"]), begin)
        comparison = {key: _change(summary[key], previous[key], key in {"conversion", "engagement_rate"})
                      for key in ("visitors", "visits", "views", "signups", "conversion", "average_time", "engagement_rate")}
    new = _count(select(func.count(func.distinct(View.visitor_id))).join(Visitor, Visitor.id == View.visitor_id)
                 .where(view_scope, Visitor.first_seen >= begin))
    summary.update(new_visitors=new, returning_visitors=max(0, summary["visitors"] - new))
    settled = or_(View.ended_at.is_not(None), Visit.last_seen < now_utc() - timedelta(seconds=current_app.config["ANALYTICS_SESSION_SECONDS"]))
    exit_rows = db.session.execute(select(View.path, func.count(View.id)).join(Visit, Visit.last_page_id == View.id)
                                   .where(view_scope, settled).group_by(View.path)).all()
    exit_counts = dict(exit_rows)
    known = _known_pages()
    pages = {path: {"path": path, "title": title, "views": 0, "visitors": 0, "average_time": 0,
                    "exits": 0, "exit_rate": 0, "timed_views": 0} for path, title in known.items()}
    for path, title, views, visitors, seconds, timed in db.session.execute(select(
            View.path, func.max(View.title), func.count(View.id), func.count(func.distinct(View.visitor_id)),
            func.sum(View.active_seconds), func.sum(cast(View.timing_received, db.Integer)))
            .where(view_scope).group_by(View.path).order_by(func.count(View.id).desc()).limit(1000)):
        exits = exit_counts.get(path, 0)
        pages[path] = {"path": path, "title": known.get(path, title), "views": views, "visitors": visitors,
                       "average_time": round(seconds / timed, 1) if timed else 0, "timed_views": timed,
                       "exits": exits, "exit_rate": round(100 * exits / views, 1) if views else 0}
    source_signups = {(source, channel, referrer): count for source, channel, referrer, count in db.session.execute(
        select(Visit.source, Visit.channel, Visit.referrer, func.count(Event.id)).join(Event, Event.visit_id == Visit.id)
        .where(event_scope, Event.name == "signup_complete").group_by(Visit.source, Visit.channel, Visit.referrer))}
    sources = []
    for source, channel, referrer, visitors, visits, views in db.session.execute(select(
            Visit.source, Visit.channel, Visit.referrer, func.count(func.distinct(View.visitor_id)),
            func.count(func.distinct(View.visit_id)), func.count(View.id))
            .join(View, View.visit_id == Visit.id).where(view_scope).group_by(Visit.source, Visit.channel, Visit.referrer)
            .order_by(func.count(func.distinct(View.visitor_id)).desc()).limit(200)):
        sources.append({"source": source, "channel": channel, "referrer": referrer, "visitors": visitors,
                        "visits": visits, "views": views, "signups": source_signups.get((source, channel, referrer), 0)})
    observed_sources = {(row["source"], row["channel"], row["referrer"]) for row in sources}
    for (source, channel, referrer), signups in source_signups.items():
        if (source, channel, referrer) not in observed_sources:
            sources.append({"source": source, "channel": channel, "referrer": referrer,
                            "visitors": 0, "visits": 0, "views": 0, "signups": signups})
    entries = [{"path": path, "title": known.get(path, title), "visits": count} for path, title, count in db.session.execute(
        select(Visit.entry_path, func.max(Visit.entry_title), func.count(Visit.id))
        .where(_between(Visit.started_at, begin, finish)).group_by(Visit.entry_path).order_by(func.count(Visit.id).desc()).limit(20))]
    exits = sorted([{"path": path, "title": pages.get(path, {}).get("title", path), "visits": count} for path, count in exit_rows],
                   key=lambda row: (-row["visits"], row["path"]))[:20]
    signup_pages = [{"path": path, "title": known.get(path, path), "signups": count} for path, count in db.session.execute(
        select(Event.attribution_page, func.count(Event.id)).where(event_scope, Event.name == "signup_complete")
        .group_by(Event.attribution_page).order_by(func.count(Event.id).desc()).limit(20))]
    important = (select(View.visit_id.label("visit"), func.min(View.created_at).label("at"))
                 .where(view_scope, View.important.is_(True)).group_by(View.visit_id).subquery())
    starts = (select(Event.visit_id.label("visit"), func.min(Event.created_at).label("at"))
              .join(important, important.c.visit == Event.visit_id)
              .where(event_scope, Event.name == "signup_start", Event.created_at >= important.c.at).group_by(Event.visit_id).subquery())
    step2 = _count(select(func.count(func.distinct(View.visitor_id))).where(view_scope, View.important.is_(True)))
    step3 = _count(select(func.count(func.distinct(Event.visitor_id))).join(important, important.c.visit == Event.visit_id)
                   .where(event_scope, Event.name == "signup_start", Event.created_at >= important.c.at))
    step4 = _count(select(func.count(func.distinct(Event.visitor_id))).join(important, important.c.visit == Event.visit_id)
                   .join(starts, starts.c.visit == Event.visit_id).where(event_scope, Event.name == "signup_complete",
                       starts.c.at >= important.c.at, Event.created_at >= starts.c.at))
    funnel = [{"label": label, "count": count} for label, count in zip(
        ["Website visitor", "Viewed a study page", "Started signup", "Completed signup"],
        [summary["visitors"], step2, step3, step4], strict=True)]
    for index, step in enumerate(funnel):
        before = funnel[index - 1]["count"] if index else summary["visitors"]
        step["progress"] = round(100 * step["count"] / summary["visitors"], 1) if summary["visitors"] else 0
        step["dropoff"] = round(100 * (before - step["count"]) / before, 1) if before and index else 0
    completed_visits = select(Event.visit_id).where(Event.name == "signup_complete")
    left_visits = select(Event.visit_id).where(Event.name == "signup_leave")
    summary["signup_starts"] = _count(select(func.count(func.distinct(Event.visit_id))).where(event_scope, Event.name == "signup_start"))
    summary["signup_abandoned"] = _count(select(func.count(func.distinct(Event.visit_id))).join(Visit, Visit.id == Event.visit_id)
        .where(event_scope, Event.name == "signup_start", Event.visit_id.not_in(completed_visits),
               or_(Event.visit_id.in_(left_visits), Visit.last_seen < now_utc() - timedelta(seconds=current_app.config["ANALYTICS_SESSION_SECONDS"]))))
    event_counts = [{"name": name, "label": label, "count": count} for name, label, count in db.session.execute(
        select(Event.name, Event.label, func.count(Event.id)).where(event_scope)
        .group_by(Event.name, Event.label).order_by(func.count(Event.id).desc()).limit(30))]
    recent = [{"event": name, "label": label, "path": path, "source": source, "at": at.isoformat() + "Z"}
              for name, label, path, source, at in db.session.execute(select(Event.name, Event.label, View.path, Visit.source, Event.created_at)
              .join(View, View.id == Event.page_id).join(Visit, Visit.id == Event.visit_id).where(event_scope)
              .order_by(Event.created_at.desc()).limit(30))]
    recent += [{"event": "page_view", "label": title, "path": path, "source": source, "at": at.isoformat() + "Z"}
               for title, path, source, at in db.session.execute(select(View.title, View.path, Visit.source, View.created_at)
               .join(Visit, Visit.id == View.visit_id).where(view_scope).order_by(View.created_at.desc()).limit(30))]
    recent.sort(key=lambda row: row["at"], reverse=True)
    recent = recent[:30]
    # Only bounded recent-session detail is read into Python, even for "All time".
    recent_visits = (select(View.visit_id).where(view_scope).group_by(View.visit_id)
                     .order_by(func.max(View.created_at).desc()).limit(500))
    ranked = select(View.visit_id, View.path, View.created_at, func.row_number().over(
        partition_by=View.visit_id, order_by=(View.created_at, View.id)).label("position"))
    ranked = ranked.where(view_scope, View.visit_id.in_(recent_visits)).subquery()
    paths = {}
    for visit, path, _, _ in db.session.execute(select(ranked).where(ranked.c.position <= 12)
                                               .order_by(ranked.c.visit_id, ranked.c.position)):
        paths.setdefault(visit, []).append(path)
    journeys = [{"pages": [{"path": path, "title": known.get(path, path)} for path in pattern], "visits": count}
                for pattern, count in Counter(tuple(value) for value in paths.values()).most_common(8)]
    lagged = select(View.visit_id, View.path, func.lag(View.path).over(
        partition_by=View.visit_id, order_by=(View.created_at, View.id)).label("previous")).where(view_scope).subquery()
    transitions = [{"from": before, "to": after, "from_title": known.get(before, before), "to_title": known.get(after, after), "visits": count}
                   for before, after, count in db.session.execute(select(lagged.c.previous, lagged.c.path, func.count(func.distinct(lagged.c.visit_id)))
                   .where(lagged.c.previous.is_not(None), lagged.c.previous != lagged.c.path)
                   .group_by(lagged.c.previous, lagged.c.path).order_by(func.count(func.distinct(lagged.c.visit_id)).desc()).limit(10))]
    today = date.fromisoformat(window["today"])
    calendar = {}
    for label, start in [("today", today), ("week", today - timedelta(days=today.weekday())), ("month", today.replace(day=1))]:
        low = datetime.combine(start, time.min, TZ).astimezone(timezone.utc).replace(tzinfo=None)
        high = datetime.combine(today + timedelta(days=1), time.min, TZ).astimezone(timezone.utc).replace(tzinfo=None)
        calendar[label] = {"visitors": _count(select(func.count(func.distinct(View.visitor_id))).where(_between(View.created_at, low, high))),
                           "signups": _count(select(func.count(User.id)).where(User.is_admin.is_(False), _between(User.created_at, low, high)))}
    first = db.session.scalar(select(func.min(View.created_at)))
    totals = {"visits": _count(select(func.count(Visit.id))), "visitors": _count(select(func.count(Visitor.id))),
              "views": _count(select(func.count(View.id))), "signups": _count(select(func.count(User.id)).where(User.is_admin.is_(False)))}
    window = {key: value for key, value in window.items() if key not in {"begin", "finish"}}
    return {"range": window, "summary": summary, "comparison": comparison, "totals": totals, "calendar": calendar,
            "tracking_since": first.isoformat() + "Z" if first else None,
            "trend": _trend(begin, finish, window["days"], window["start"], window["end"]),
            "pages": sorted(pages.values(), key=lambda row: (-row["views"], row["path"])),
            "sources": sources, "entries": entries, "exits": exits, "signup_pages": signup_pages,
            "unattributed_signups": max(0, summary["signups"] - summary["tracked_signups"]),
            "funnel": funnel, "event_counts": event_counts, "recent": recent, "journeys": journeys,
            "journeys_sample": len(paths), "transitions": transitions}
