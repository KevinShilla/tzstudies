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

from tzstudies.extensions import mail

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload_exams", methods=["GET", "POST"])
def upload_exams():
    if request.method == "POST":
        pdf = request.files.get("exam_pdf")
        if not pdf or not pdf.filename.lower().endswith(".pdf"):
            flash("Please upload a valid PDF file.", "error")
            return redirect(url_for("upload.upload_exams"))

        if pdf.read(5) != b"%PDF-":
            flash("Please choose a readable PDF file.", "error")
            return redirect(url_for("upload.upload_exams"))
        pdf.seek(0)

        recipient = current_app.config.get("MAIL_USERNAME")
        if not recipient:
            flash("Paper submissions are temporarily unavailable. Please try again later.", "error")
            return redirect(url_for("upload.upload_exams"))

        msg = Message(
            subject="New exam uploaded",
            recipients=[recipient],
        )
        filename = secure_filename(pdf.filename) or "exam.pdf"
        msg.body = f"A user uploaded: {filename}"
        msg.attach(filename, "application/pdf", pdf.read())
        try:
            mail.send(msg)
        except Exception:
            current_app.logger.exception("Could not send contributed exam")
            flash("We couldn't send your paper. Please try again later.", "error")
            return redirect(url_for("upload.upload_exams"))

        flash("Thank you! Your file has been sent to the team.", "success")
        return redirect(url_for("papers.index"))

    return render_template("upload_exams.html")
