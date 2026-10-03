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

from tzstudies.extensions import db, limiter
from tzstudies.file_security import cv_folder, read_document, store_cv
from tzstudies.models import TutorApplication
from tzstudies.security import valid_email, valid_text
from tzstudies.tutor_directory import TUTORS

tutors_bp = Blueprint("tutors", __name__)

@tutors_bp.route("/tutors")
def tutors_page():
    return render_template(
        "tutors.html", tutors=TUTORS,
        subjects=sorted({subject for tutor in TUTORS for subject in tutor["subjects"]}),
    )


@tutors_bp.route("/become_tutor", methods=["GET", "POST"])
@limiter.limit("3 per hour", methods=["POST"])
def become_tutor():
    if request.method == "POST":
        limits = {
            "name": 255, "location": 255, "school": 255, "hourly_rate": 50,
            "experience": 255, "classes_taught": 255, "email": 255,
            "profile_bio": 4000,
        }
        form = {field: request.form.get(field, "").strip() for field in limits}
        if any(not valid_text(value, limits[field], multiline=field == "profile_bio") for field, value in form.items()):
            flash("Please complete every required field and keep your profile under 4,000 characters.", "error")
            return redirect(url_for("tutors.become_tutor"))
        if not valid_email(form["email"], 255):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("tutors.become_tutor"))
        phone = request.form.get("phone", "").strip()
        if phone and not valid_text(phone, 50):
            flash("Please enter a shorter phone number.", "error")
            return redirect(url_for("tutors.become_tutor"))

        # Handle CV file upload
        cv_filename = None
        cv_file = request.files.get("cv_file")
        if cv_file and cv_file.filename:
            try:
                data, suffix = read_document(cv_file, allowed=(".pdf", ".docx"))
                cv_filename = store_cv(data, suffix)
            except ValueError as exc:
                flash(str(exc), "error")
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
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            if cv_filename:
                (cv_folder() / cv_filename).unlink(missing_ok=True)
            current_app.logger.error("Tutor application could not be saved")
            flash("We couldn't save your application. Please try again shortly.", "error")
            return redirect(url_for("tutors.become_tutor"))
        flash("Application submitted! We'll review it shortly.", "success")
        return redirect(url_for("tutors.tutors_page"))

    return render_template("become_tutor.html")


@tutors_bp.route("/api/v1/tutors")
def api_tutors():
    # Applications contain private contact and CV data; publish curated profiles only.
    data = [dict(tutor, id=index) for index, tutor in enumerate(TUTORS, start=1)]
    return jsonify({"tutors": data, "count": len(data)})
