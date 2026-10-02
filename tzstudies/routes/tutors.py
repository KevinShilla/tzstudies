import os
from uuid import uuid4

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from tzstudies.extensions import db
from tzstudies.models import TutorApplication
from tzstudies.tutor_directory import TUTORS

tutors_bp = Blueprint("tutors", __name__)

ALLOWED_CV_EXTENSIONS = {"pdf", "doc", "docx"}


def _allowed_cv(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_CV_EXTENSIONS


def _get_cv_folder():
    folder = os.path.join(current_app.root_path, os.pardir, "uploads", "cvs")
    os.makedirs(folder, exist_ok=True)
    return folder


@tutors_bp.route("/tutors")
def tutors_page():
    return render_template(
        "tutors.html", tutors=TUTORS,
        subjects=sorted({subject for tutor in TUTORS for subject in tutor["subjects"]}),
    )


@tutors_bp.route("/become_tutor", methods=["GET", "POST"])
def become_tutor():
    if request.method == "POST":
        limits = {
            "name": 255, "location": 255, "school": 255, "hourly_rate": 50,
            "experience": 255, "classes_taught": 255, "email": 255,
            "profile_bio": 4000,
        }
        form = {field: request.form.get(field, "").strip() for field in limits}
        if any(not value or len(value) > limits[field] for field, value in form.items()):
            flash("Please complete every required field and keep your profile under 4,000 characters.", "error")
            return redirect(url_for("tutors.become_tutor"))
        if "@" not in form["email"] or any(c.isspace() for c in form["email"]):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("tutors.become_tutor"))
        phone = request.form.get("phone", "").strip()
        if len(phone) > 50:
            flash("Please enter a shorter phone number.", "error")
            return redirect(url_for("tutors.become_tutor"))

        # Handle CV file upload
        cv_filename = None
        cv_file = request.files.get("cv_file")
        if cv_file and cv_file.filename and _allowed_cv(cv_file.filename):
            safe_name = secure_filename(cv_file.filename)
            cv_filename = f"{uuid4().hex}-{safe_name[-210:]}"
            cv_file.save(os.path.join(_get_cv_folder(), cv_filename))
        elif cv_file and cv_file.filename:
            flash("Invalid file type. Please upload a PDF or Word document.", "error")
            return redirect(url_for("tutors.become_tutor"))

        app_row = TutorApplication(
            name=form["name"],
            location=form["location"],
            school=form["school"],
            hourly_rate=form["hourly_rate"],
            experience=form["experience"],
            classes_taught=form["classes_taught"],
            phone=phone,
            email=form["email"],
            cv_filename=cv_filename,
            profile_bio=form["profile_bio"],
        )
        db.session.add(app_row)
        db.session.commit()
        flash("Application submitted! We'll review it shortly.", "success")
        return redirect(url_for("tutors.tutors_page"))

    return render_template("become_tutor.html")


@tutors_bp.route("/api/v1/tutors")
def api_tutors():
    # Applications contain private contact and CV data; publish curated profiles only.
    data = [dict(tutor, id=index) for index, tutor in enumerate(TUTORS, start=1)]
    return jsonify({"tutors": data, "count": len(data)})
