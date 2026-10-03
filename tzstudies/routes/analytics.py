from flask import Blueprint, abort, current_app, jsonify, make_response, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from tzstudies.analytics import (
    COOKIE_AGE,
    OPTOUT_COOKIE,
    VISIT_COOKIE,
    VISITOR_COOKIE,
    collect,
    parse_collect_request,
    read_ticket,
    refresh_visit_cookie,
    tracking_allowed,
    validate_payload,
)
from tzstudies.analytics_reports import report
from tzstudies.extensions import db, limiter
from tzstudies.routes.admin import admin_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/collect", methods=["POST"])
@limiter.limit("300 per hour; 40 per minute")
def ingest():
    # CSRF remains enabled, including beacon FormData. Reject cross-origin requests too.
    if request.headers.get("Sec-Fetch-Site") == "cross-site" or (
            request.headers.get("Origin") and request.headers["Origin"].rstrip("/") != request.host_url.rstrip("/")):
        abort(403)
    if not tracking_allowed():
        return "", 204
    raw = parse_collect_request()
    payload = validate_payload(raw)
    data = read_ticket(raw.get("ticket")) if isinstance(raw, dict) else None
    if not payload or not data:
        return jsonify(error="Invalid analytics payload."), 400
    if not collect(data, payload):
        return jsonify(error="Analytics temporarily unavailable."), 503
    response = make_response("", 204)
    return refresh_visit_cookie(response, data) if payload["state"] == "active" else response


@analytics_bp.route("/admin/analytics")
@admin_required
def dashboard():
    return render_template("admin/analytics.html")


@analytics_bp.route("/admin/analytics/data")
@admin_required
@limiter.limit("30 per minute; 300 per hour")
def data():
    try:
        response = jsonify(report(request.args))
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.warning("Analytics report unavailable")
        return jsonify(error="Analytics is temporarily unavailable. Please refresh in a moment."), 503
    response.headers["Cache-Control"] = "no-store, private"
    return response


@analytics_bp.route("/privacy")
def privacy():
    return render_template("privacy.html", opted_out=request.cookies.get(OPTOUT_COOKIE) == "1")


@analytics_bp.route("/analytics/preferences", methods=["POST"])
def preferences():
    if request.form.get("choice") not in {"off", "on"}:
        abort(400)
    response = redirect(url_for("analytics.privacy"))
    if request.form["choice"] == "off":
        response.set_cookie(OPTOUT_COOKIE, "1", max_age=COOKIE_AGE, httponly=True,
                            secure=current_app.config.get("SESSION_COOKIE_SECURE", False), samesite="Lax")
        response.delete_cookie(VISITOR_COOKIE)
        response.delete_cookie(VISIT_COOKIE)
    else:
        response.delete_cookie(OPTOUT_COOKIE)
    return response
