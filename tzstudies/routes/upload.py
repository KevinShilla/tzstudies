from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, url_for,
)
from flask_mail import Message

from tzstudies.extensions import mail

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload_exams", methods=["GET", "POST"])
def upload_exams():
    if request.method == "POST":
        pdf = request.files.get("exam_pdf")
        if not pdf or not pdf.filename.lower().endswith(".pdf"):
            flash("Please upload a valid PDF file.", "error")
            return redirect(url_for("upload.upload_exams"))

        recipient = current_app.config.get("MAIL_USERNAME")
        if not recipient:
            flash("Email service is not configured.", "error")
            return redirect(url_for("upload.upload_exams"))

        msg = Message(
            subject="New exam uploaded",
            recipients=[recipient],
        )
        msg.body = f"A user uploaded: {pdf.filename}"
        msg.attach(pdf.filename, pdf.mimetype, pdf.read())
        mail.send(msg)

        flash("Thank you! Your file has been sent to the team.", "success")
        return redirect(url_for("papers.index"))

    return render_template("upload_exams.html")
