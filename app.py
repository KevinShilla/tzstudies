<<<<<<< HEAD
"""Entry point for TZStudies.

Usage:
    Development:  python app.py
    Production:   gunicorn "tzstudies:create_app()"
"""

from tzstudies import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
=======
import os
import re
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, abort,
    jsonify, send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import openai
from config import Config

# ── Flask & core config ───────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)                        
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
}

# ── extensions ────────────────────────────────────────────────────────
db   = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

openai.api_key = os.getenv("OPENAI_API_KEY", "")

# ── filesystem paths ─────────────────────────────────────────────────
ROOT_DIR            = os.getcwd()
EXAMS_FOLDER        = os.path.join(ROOT_DIR, "exams")
ANSWER_KEYS_FOLDER  = os.path.join(ROOT_DIR, "answer_keys")
CV_UPLOAD_FOLDER    = os.path.join(ROOT_DIR, "uploads", "cvs")

os.makedirs(CV_UPLOAD_FOLDER, exist_ok=True)

# ── database models ──────────────────────────────────────────────────
class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    name       = db.Column(db.String(100))
    pw_hash    = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    history    = db.relationship("History", backref="user", lazy=True)

class Paper(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(150), unique=True)
    category  = db.Column(db.String(20))   # exam / key
    grade     = db.Column(db.String(10))

class History(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("user.id"))
    paper_id  = db.Column(db.Integer, db.ForeignKey("paper.id"))
    event     = db.Column(db.String(10))   # view / download
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    paper     = db.relationship("Paper")

class TutorApplication(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(255), nullable=False)
    location       = db.Column(db.String(255), nullable=False)
    school         = db.Column(db.String(255), nullable=False)
    hourly_rate    = db.Column(db.String(50),  nullable=False)
    experience     = db.Column(db.String(255), nullable=False)
    classes_taught = db.Column(db.String(255), nullable=False)
    phone          = db.Column(db.String(50))
    email          = db.Column(db.String(255), nullable=False)
    cv_bio         = db.Column(db.Text, nullable=False)
    profile_bio    = db.Column(db.Text, nullable=False)

# ── one‑time table creation ──────────────────────────────────────────
with app.app_context():
    db.create_all()

# ── auth helpers & routes ────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("E‑mail already registered", "error")
            return redirect(url_for("signup"))
        user = User(
            email=request.form["email"],
            name=request.form["name"],
            pw_hash=generate_password_hash(request.form["password"])
        )
        db.session.add(user); db.session.commit(); login_user(user)
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.pw_hash, request.form["password"]):
            login_user(user); return redirect(url_for("index"))
        flash("Wrong credentials", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user(); return redirect(url_for("index"))

# ── history page (last 15) ──────────────────────────────────────────
@app.route("/history")
@login_required
def history():
    rows = (History.query
            .filter_by(user_id=current_user.id)
            .order_by(History.viewed_at.desc())
            .limit(15).all())
    return render_template("history.html", rows=rows)

# ── main public pages ────────────────────────────────────────────────
@app.route("/")
def index():
    exam_files = [f for f in os.listdir(EXAMS_FOLDER) if f.lower().endswith(".pdf")]
    answer_key_files = {}
    if os.path.exists(ANSWER_KEYS_FOLDER):
        for f in os.listdir(ANSWER_KEYS_FOLDER):
            if f.lower().endswith(".pdf"):
                base = f.replace(" (Answer Key)", "")
                answer_key_files[base] = f
    return render_template(
        "index.html",
        exam_files=exam_files,
        answer_key_files=answer_key_files
    )

# ========= helper =================================================
def _log_and_send(filename: str, folder: str, event: str):
    """
    • Makes sure a Paper row exists
    • Logs the view/download for logged-in users
    • Streams the file from the given folder
    """
    paper = Paper.query.filter_by(file_name=filename).first()
    if not paper:
        cat   = "key" if folder == ANSWER_KEYS_FOLDER else "exam"
        grade = filename.split("-")[1] if "-" in filename else ""
        paper = Paper(file_name=filename, category=cat, grade=grade)
        db.session.add(paper)
        db.session.commit()

    if current_user.is_authenticated:
        db.session.add(
            History(user_id=current_user.id, paper_id=paper.id, event=event)
        )
        db.session.commit()

    return send_from_directory(folder, filename, as_attachment=True)

# ========= routes =================================================
@app.route("/download/<path:filename>")
def download(filename):
    return _log_and_send(filename, EXAMS_FOLDER, "download")

@app.route("/download_key/<path:filename>")
@login_required
def download_key(filename):
    return _log_and_send(filename, ANSWER_KEYS_FOLDER, "download")

# ── tutors & applications --------------------------------------------------
@app.route("/tutors")
def tutors():
    return render_template("tutors.html")

@app.route("/become_tutor", methods=["GET", "POST"])
def become_tutor():
    if request.method == "POST":
        form = request.form
        app_row = TutorApplication(
            name=form["name"], location=form["location"], school=form["school"],
            hourly_rate=form["hourly_rate"], experience=form["experience"],
            classes_taught=form["classes_taught"], phone=form.get("phone"),
            email=form["email"], cv_bio=form.get("cv_bio", ""), profile_bio=form["profile_bio"]
        )
        db.session.add(app_row); db.session.commit()
        flash("Application submitted!", "success")
        return redirect(url_for("tutors"))
    return render_template("become_tutor.html")

@app.route("/view/<path:filename>")
def view_exam(filename):
    _log_and_send(filename, EXAMS_FOLDER, "view")  # event = view
    return render_template("view_exam.html", filename=filename)

# ── upload exams (email notification) --------------------------------------
@app.route("/upload_exams", methods=["GET", "POST"])
def upload_exams():
    if request.method == "POST":
        pdf = request.files.get("exam_pdf")
        if not pdf or not pdf.filename.lower().endswith(".pdf"):
            flash("Please upload a valid PDF file.", "error")
            return redirect(url_for("upload_exams"))
        msg = Message(
            subject="New exam uploaded",
            recipients=[app.config["MAIL_USERNAME"]]
        )
        msg.body = f"User uploaded: {pdf.filename}"
        msg.attach(pdf.filename, pdf.mimetype, pdf.read())
        mail.send(msg)
        flash("Thank you! Your file has been sent to the team.", "success")
        return redirect(url_for("index"))
    return render_template("upload_exams.html")

# ── OpenAI exam Q&A ---------------------------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Answer the following exam question in detail: {query}"}],
        max_tokens=250,
        temperature=0.7
    )
    return jsonify({"answer": resp.choices[0].message["content"].strip()})

# ── tutors API --------------------------------------------------------------
@app.route("/api/tutors")
def api_tutors():
    data = [
        {
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "school": t.school,
            "hourly_rate": t.hourly_rate,
            "experience": t.experience,
            "classes_taught": t.classes_taught,
            "phone": t.phone,
            "email": t.email,
            "cv_bio": t.cv_bio,
            "profile_bio": t.profile_bio
        } for t in TutorApplication.query.all()]
    return jsonify(data)

# ── answer keys listing page ------------------------------------------------

# ── papers API + React demo -------------------------------------------------
def _parse_paper_filename(filename: str):
    """Best-effort parser for filenames like:
       - BasicMath-F2-2021.pdf
       - English - S7 - 2016.pdf
    Returns: subject, level, year (strings)
    """
    name = filename.replace(".pdf", "")
    # normalize separators to "-"
    cleaned = re.sub(r"\s*-\s*", "-", name.strip())
    cleaned = re.sub(r"\s+", " ", cleaned).replace(" - ", "-")
    # now split on "-"
    parts = [p.strip() for p in cleaned.split("-") if p.strip()]
    subject, level, year = "", "", ""
    if len(parts) >= 3:
        subject = parts[0]
        level = parts[1]
        year = parts[2]
    elif len(parts) == 2:
        subject = parts[0]
        level = parts[1]
    else:
        subject = name
    return subject, level, year

@app.route("/api/papers")
def get_papers():
    import os
    papers = []

    if not os.path.exists(EXAMS_FOLDER):
        return jsonify(papers)

    for subject in os.listdir(EXAMS_FOLDER):
        subject_path = os.path.join(EXAMS_FOLDER, subject)
        if not os.path.isdir(subject_path):
            continue

        for level in os.listdir(subject_path):
            level_path = os.path.join(subject_path, level)
            if not os.path.isdir(level_path):
                continue

            for year in os.listdir(level_path):
                year_path = os.path.join(level_path, year)
                if not os.path.isdir(year_path):
                    continue

                for file in os.listdir(year_path):
                    if file.endswith(".pdf"):
                        papers.append({
                            "subject": subject,
                            "level": level,
                            "year": year,
                            "name": file,
                            "view_url": f"/view_exam/{subject}/{level}/{year}/{file}",
                            "download_url": f"/download_exam/{subject}/{level}/{year}/{file}",
                            "answer_key": None
                        })

    return jsonify(papers)

@app.route("/react_library")
def react_library():
    return render_template("react_library.html")


@app.route("/answer_keys")
def answer_keys_page():
    keys = [f for f in os.listdir(ANSWER_KEYS_FOLDER) if f.lower().endswith(".pdf")] if os.path.exists(ANSWER_KEYS_FOLDER) else []
    return render_template("answer_keys.html", keys=keys)

# ── run local ----------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> b0f630e630adb5cf1db102ce373ade117d49b2ab
