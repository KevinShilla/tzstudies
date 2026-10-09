import os

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from tzstudies.catalogue import build_catalogue, identity, metadata
from tzstudies.extensions import db, limiter
from tzstudies.library import library_context
from tzstudies.models import Comment, History, Paper
from tzstudies.security import valid_text

papers_bp = Blueprint("papers", __name__)


def _get_exams_folder():
    return os.path.join(current_app.root_path, os.pardir, "exams")


def _get_answer_keys_folder():
    return os.path.join(current_app.root_path, os.pardir, "answer_keys")


def _ensure_paper(filename, folder, category):
    """Return a Paper row, creating one if it doesn't exist yet."""
    _require_pdf(filename, folder)
    paper = Paper.query.filter_by(file_name=filename).first()
    if not paper:
        grade = metadata(filename)["grade"]
        paper = Paper(file_name=filename, category=category, grade=grade)
        db.session.add(paper)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            paper = Paper.query.filter_by(file_name=filename).first()
            if not paper:
                raise
    return paper


def _log_event(paper, event):
    """Log a view/download event for the current user."""
    if current_user.is_authenticated:
        db.session.add(
            History(user_id=current_user.id, paper_id=paper.id, event=event)
        )
        db.session.commit()


def _require_pdf(filename, folder):
    from pathlib import Path
    root = Path(folder).resolve()
    path = (root / filename).resolve()
    if len(filename) > 200 or "/" in filename or "\\" in filename or not path.is_relative_to(root) or not path.is_file() or path.suffix.lower() != ".pdf":
        abort(404)
    return path


def _catalogue():
    return build_catalogue(_get_exams_folder(), _get_answer_keys_folder())


def _sync_papers(exams, retry=True):
    existing = {p.file_name: p for p in Paper.query.filter_by(category="exam").all()}
    for exam in exams:
        paper = existing.get(exam["filename"])
        if paper is None:
            paper = Paper(file_name=exam["filename"], category="exam", grade=exam["grade"])
            db.session.add(paper)
        exam["paper"] = paper
    try:
        if db.session.new:
            db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if not retry:
            raise
        return _sync_papers(exams, retry=False)
    for exam in exams:
        exam["paper_id"] = exam.pop("paper").id


@papers_bp.route("/")
def index():
    exams = _catalogue()
    return render_template(
        "index.html",
        **library_context(exams),
        ai_available=bool(current_app.config.get("OPENAI_API_KEY")),
    )


@papers_bp.route("/view/<path:filename>")
def view_exam(filename):
    folder = _get_exams_folder()
    paper = _ensure_paper(filename, folder, "exam")
    _log_event(paper, "view")
    exam = next((e for e in _catalogue() if identity(e["filename"]) == identity(filename)), metadata(filename))
    return render_template("view_exam.html", filename=filename, exam=exam)


@papers_bp.route("/serve/<path:filename>")
def serve_pdf(filename):
    """Serve a PDF inline for embedding in iframes (no download prompt)."""
    folder = _get_exams_folder()
    _require_pdf(filename, folder)
    return send_from_directory(
        os.path.abspath(folder), filename, as_attachment=False, conditional=True, max_age=86400
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
    exams = _catalogue()
    return render_template("answer_keys.html", **library_context(exams, endpoint="papers.answer_keys_page", answer_keys=True))


@papers_bp.route("/view_key/<path:filename>")
@login_required
def view_key(filename):
    _ensure_paper(filename, _get_answer_keys_folder(), "key")
    exam = next((e for e in _catalogue() if identity(e["filename"]) == identity(filename)), metadata(filename))
    return render_template("view_key.html", filename=filename, exam=exam)


@papers_bp.route("/serve_key/<path:filename>")
@login_required
def serve_key(filename):
    _require_pdf(filename, _get_answer_keys_folder())
    return send_from_directory(os.path.abspath(_get_answer_keys_folder()), filename, as_attachment=False)


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
    if len(q) > 200 or (q and not valid_text(q, 200)):
        abort(400)
    if not q:
        return redirect(url_for("papers.index"))
    exams = _catalogue()
    return render_template("search_results.html", **library_context(exams, endpoint="papers.search"), query=q)


@papers_bp.route("/paper/<int:paper_id>")
def paper_detail(paper_id):
    paper = db.get_or_404(Paper, paper_id)
    if paper.category == "key" and not current_user.is_authenticated:
        return current_app.login_manager.unauthorized()
    folder = _get_answer_keys_folder() if paper.category == "key" else _get_exams_folder()
    _require_pdf(paper.file_name, folder)
    _log_event(paper, "view")
    comments = (
        Comment.query
        .filter_by(paper_id=paper.id, parent_id=None)
        .order_by(Comment.created_at.asc())
        .all()
    )
    exam = next((entry for entry in _catalogue() if identity(entry["filename"]) == identity(paper.file_name)), metadata(paper.file_name))
    return render_template("paper_detail.html", paper=paper, comments=comments, exam=exam)


@papers_bp.route("/paper/<int:paper_id>/comment", methods=["POST"])
@login_required
@limiter.limit("10 per hour")
def post_comment(paper_id):
    paper = db.get_or_404(Paper, paper_id)
    body = request.form.get("body", "").strip()
    if not body:
        flash("Comment cannot be empty.", "error")
        return redirect(url_for("papers.paper_detail", paper_id=paper_id))
    if not valid_text(body, 2000, multiline=True):
        flash("Comment is too long (max 2000 characters).", "error")
        return redirect(url_for("papers.paper_detail", paper_id=paper_id))

    raw_parent = request.form.get("parent_id", "")
    if raw_parent and (not raw_parent.isascii() or not raw_parent.isdigit() or len(raw_parent) > 10 or not 1 <= int(raw_parent) <= 2147483647):
        abort(400)
    parent_id = int(raw_parent) if raw_parent else None
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


@papers_bp.route("/about")
def about():
    exams = _catalogue()
    return render_template(
        "about.html", paper_count=len(exams),
        level_count=len({exam["grade"] for exam in exams}),
    )
