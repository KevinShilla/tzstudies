import os

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request,
    send_from_directory, url_for,
)
from flask_login import current_user, login_required

from tzstudies.extensions import cache, db, limiter
from tzstudies.models import Comment, History, Paper

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

    # Ensure every exam file has a database row and collect paper IDs
    paper_ids = {}
    for f in exam_files:
        paper = _ensure_paper(f, exams_folder, "exam")
        paper_ids[f] = paper.id

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
        paper_ids=paper_ids,
    )


@papers_bp.route("/view/<path:filename>")
def view_exam(filename):
    folder = _get_exams_folder()
    paper = _ensure_paper(filename, folder, "exam")
    _log_event(paper, "view")
    return render_template("view_exam.html", filename=filename)


@papers_bp.route("/serve/<path:filename>")
def serve_pdf(filename):
    """Serve a PDF inline for embedding in iframes (no download prompt)."""
    folder = _get_exams_folder()
    return send_from_directory(
        os.path.abspath(folder), filename, as_attachment=False
    )


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


@papers_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return redirect(url_for("papers.index"))
    results = (
        Paper.query
        .filter(Paper.category == "exam")
        .filter(Paper.file_name.ilike(f"%{q}%"))
        .order_by(Paper.file_name.asc())
        .all()
    )
    return render_template("search_results.html", results=results, query=q)


@papers_bp.route("/paper/<int:paper_id>")
def paper_detail(paper_id):
    paper = db.get_or_404(Paper, paper_id)
    _log_event(paper, "view")
    comments = (
        Comment.query
        .filter_by(paper_id=paper.id, parent_id=None)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return render_template("paper_detail.html", paper=paper, comments=comments)


@papers_bp.route("/paper/<int:paper_id>/comment", methods=["POST"])
@login_required
@limiter.limit("10 per hour")
def post_comment(paper_id):
    paper = db.get_or_404(Paper, paper_id)
    body = request.form.get("body", "").strip()
    if not body:
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("papers.paper_detail", paper_id=paper_id))
    if len(body) > 2000:
        flash("Comment is too long (max 2000 characters).", "error")
        return redirect(url_for("papers.paper_detail", paper_id=paper_id))

    parent_id = request.form.get("parent_id", type=int)
    if parent_id:
        parent = Comment.query.filter_by(id=parent_id, paper_id=paper.id).first()
        if not parent:
            flash("Invalid reply target.", "error")
            return redirect(url_for("papers.paper_detail", paper_id=paper_id))

    comment = Comment(
        paper_id=paper.id,
        user_id=current_user.id,
        parent_id=parent_id,
        body=body,
    )
    db.session.add(comment)
    db.session.commit()
    flash("Comment posted!", "success")
    return redirect(url_for("papers.paper_detail", paper_id=paper_id))


@papers_bp.route("/offline")
def offline():
    return render_template("offline.html")


@papers_bp.route("/sw.js")
def service_worker():
    root = os.path.join(current_app.root_path, os.pardir, "static")
    response = send_from_directory(os.path.abspath(root), "sw.js")
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response
