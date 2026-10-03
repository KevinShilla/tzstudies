import functools

from flask import Blueprint, abort, jsonify, render_template, send_file
from flask_login import current_user, login_required

from tzstudies.extensions import db
from tzstudies.file_security import cv_folder
from tzstudies.models import History, Paper, TutorApplication, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/cv/<int:application_id>")
@login_required
def download_cv(application_id):
    if not current_user.is_admin:
        abort(403)
    application = db.get_or_404(TutorApplication, application_id)
    if not application.cv_filename:
        abort(404)
    folder = cv_folder()
    path = (folder / application.cv_filename).resolve()
    if path.parent != folder or not path.is_file() or path.suffix not in (".pdf", ".docx", ".doc"):
        abort(404)
    response = send_file(path, as_attachment=True, download_name="tutor-cv" + path.suffix)
    response.headers["Cache-Control"] = "no-store, private"
    return response


def admin_required(f):
    """Decorator: require authenticated admin user."""
    @functools.wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "total_users": User.query.count(),
        "total_papers": Paper.query.count(),
        "total_downloads": History.query.filter_by(event="download").count(),
        "total_views": History.query.filter_by(event="view").count(),
        "tutor_applications": TutorApplication.query.count(),
    }
    recent_users = (
        User.query.order_by(User.created_at.desc()).limit(10).all()
    )
    recent_activity = (
        History.query.order_by(History.viewed_at.desc()).limit(20).all()
    )
    tutor_apps = (
        TutorApplication.query.order_by(TutorApplication.created_at.desc()).limit(10).all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        recent_activity=recent_activity,
        tutor_apps=tutor_apps,
    )


@admin_bp.route("/api/stats")
@admin_required
def api_stats():
    """JSON endpoint for dashboard data (useful for charts)."""
    from sqlalchemy import func

    # Downloads per paper (top 10)
    top_papers = (
        db.session.query(Paper.file_name, func.count(History.id))
        .join(History, History.paper_id == Paper.id)
        .filter(History.event == "download")
        .group_by(Paper.file_name)
        .order_by(func.count(History.id).desc())
        .limit(10)
        .all()
    )

    return jsonify({
        "total_users": User.query.count(),
        "total_papers": Paper.query.count(),
        "total_downloads": History.query.filter_by(event="download").count(),
        "total_views": History.query.filter_by(event="view").count(),
        "tutor_applications": TutorApplication.query.count(),
        "top_papers": [
            {"name": name, "downloads": count}
            for name, count in top_papers
        ],
    })
