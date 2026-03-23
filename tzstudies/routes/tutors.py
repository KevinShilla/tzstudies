import os

from flask import (
    Blueprint, current_app, flash, jsonify, redirect,
    render_template, request, url_for,
)
from werkzeug.utils import secure_filename

from tzstudies.extensions import db
from tzstudies.models import TutorApplication

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
    return render_template("tutors.html")


@tutors_bp.route("/become_tutor", methods=["GET", "POST"])
def become_tutor():
    if request.method == "POST":
        form = request.form

        # Handle CV file upload
        cv_filename = None
        cv_file = request.files.get("cv_file")
        if cv_file and cv_file.filename and _allowed_cv(cv_file.filename):
            cv_filename = secure_filename(cv_file.filename)
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
            phone=form.get("phone"),
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
    data = [
        {
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "school": t.school,
            "hourly_rate": t.hourly_rate,
            "experience": t.experience,
            "classes_taught": t.classes_taught,
            "email": t.email,
            "profile_bio": t.profile_bio,
        }
        for t in TutorApplication.query.all()
    ]
    return jsonify({"tutors": data, "count": len(data)})
