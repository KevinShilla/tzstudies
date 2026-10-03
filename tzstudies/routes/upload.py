from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_mail import Message
from werkzeug.utils import secure_filename

from tzstudies.extensions import limiter, mail
from tzstudies.file_security import read_document

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload_exams", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def upload_exams():
    if request.method == "POST":
        pdf = request.files.get("exam_pdf")
        if not pdf or not pdf.filename.lower().endswith(".pdf"):
            flash("Please upload a valid PDF file.", "error")
            return redirect(url_for("upload.upload_exams"))

        try:
            data, _ = read_document(pdf)
        except ValueError:
            flash("Please choose a readable PDF file under 10 MB, without scripts or embedded files.", "error")
            return redirect(url_for("upload.upload_exams"))

        recipient = current_app.config.get("MAIL_USERNAME")
        if not recipient:
            flash("Paper submissions are temporarily unavailable. Please try again later.", "error")
            return redirect(url_for("upload.upload_exams"))

        msg = Message(
            subject="New exam uploaded",
            recipients=[recipient],
        )
        filename = (secure_filename(pdf.filename) or "exam.pdf")[-180:]
        msg.body = f"A user uploaded: {filename}"
        msg.attach(filename, "application/pdf", data)
        try:
            mail.send(msg)
        except Exception:
            current_app.logger.error("Could not send contributed exam")
            flash("We couldn't send your paper. Please try again later.", "error")
            return redirect(url_for("upload.upload_exams"))

        flash("Thank you! Your file has been sent to the team.", "success")
        return redirect(url_for("papers.index"))

    return render_template("upload_exams.html")
