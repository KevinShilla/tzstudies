import os

from flask import (
    Blueprint, current_app, render_template, send_from_directory,
)
from flask_login import current_user, login_required

from tzstudies.extensions import cache, db
from tzstudies.models import History, Paper

papers_bp = Blueprint("papers", __name__)


def _get_exams_folder():
    return os.path.join(current_app.root_path, os.pardir, "exams")


def _get_answer_keys_folder():
    return os.path.join(current_app.root_path, os.pardir, "answer_keys")


def _ensure_paper(filename, folder, category):
    """Return a Paper row, creating one if it doesn't exist yet."""
    paper = Paper.query.filter_by(file_name=filename).first()
    if not paper:
        grade = filename.split("-")[1] if "-" in filename else ""
        paper = Paper(file_name=filename, category=category, grade=grade)
        db.session.add(paper)
        db.session.commit()
    return paper


def _log_event(paper, event):
    """Log a view/download event for the current user."""
    if current_user.is_authenticated:
        db.session.add(
            History(user_id=current_user.id, paper_id=paper.id, event=event)
        )
        db.session.commit()


def _index_cache_key():
    """Vary cache by authentication state so logged-in users see their navbar."""
    if current_user.is_authenticated:
        return f"view//user_{current_user.id}"
    return "view//anon"


@papers_bp.route("/")
@cache.cached(timeout=60, key_prefix=_index_cache_key)
def index():
    exams_folder = _get_exams_folder()
    exam_files = sorted(
        f for f in os.listdir(exams_folder) if f.lower().endswith(".pdf")
    )

    answer_key_files = {}
    keys_folder = _get_answer_keys_folder()
    if os.path.exists(keys_folder):
        for f in os.listdir(keys_folder):
            if f.lower().endswith(".pdf"):
                base = f.replace(" (Answer Key)", "")
                answer_key_files[base] = f

    return render_template(
        "index.html",
        exam_files=exam_files,
        answer_key_files=answer_key_files,
    )


@papers_bp.route("/view/<path:filename>")
def view_exam(filename):
    folder = _get_exams_folder()
    paper = _ensure_paper(filename, folder, "exam")
    _log_event(paper, "view")
    return render_template("view_exam.html", filename=filename)


@papers_bp.route("/download/<path:filename>")
def download(filename):
    folder = _get_exams_folder()
    paper = _ensure_paper(filename, folder, "exam")
    _log_event(paper, "download")
    return send_from_directory(
        os.path.abspath(folder), filename, as_attachment=True
    )


@papers_bp.route("/download_key/<path:filename>")
@login_required
def download_key(filename):
    folder = _get_answer_keys_folder()
    paper = _ensure_paper(filename, folder, "key")
    _log_event(paper, "download")
    return send_from_directory(
        os.path.abspath(folder), filename, as_attachment=True
    )


@papers_bp.route("/answer_keys")
def answer_keys_page():
    keys_folder = _get_answer_keys_folder()
    keys = sorted(
        f for f in os.listdir(keys_folder) if f.lower().endswith(".pdf")
    ) if os.path.exists(keys_folder) else []
    return render_template("answer_keys.html", keys=keys)


@papers_bp.route("/history")
@login_required
def history():
    rows = (
        History.query
        .filter_by(user_id=current_user.id)
        .order_by(History.viewed_at.desc())
        .limit(15)
        .all()
    )
    return render_template("history.html", rows=rows)
