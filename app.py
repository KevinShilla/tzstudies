import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from config import Config
import openai
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

# Secret key for sessions and flash messages
app.secret_key = os.getenv('SECRET_KEY', 'dev-key')

# Mail configuration (Gmail SMTP)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=('Tutor Application', os.getenv('MAIL_USERNAME'))
)
mail = Mail(app)

# Database initialization
db = SQLAlchemy(app)

# Models
class TutorApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(255), nullable=False)
    classes_taught = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255), nullable=False)
    cv_bio = db.Column(db.Text, nullable=False)
    profile_bio = db.Column(db.Text, nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# File storage folders
EXAMS_FOLDER = os.path.join(os.getcwd(), "exams")
ANSWER_KEYS_FOLDER = os.path.join(os.getcwd(), "answer_keys")
CV_UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "cvs")
if not os.path.exists(CV_UPLOAD_FOLDER):
    os.makedirs(CV_UPLOAD_FOLDER)

# Routes
@app.route('/')
def index():
    exam_files = [f for f in os.listdir(EXAMS_FOLDER) if f.lower().endswith('.pdf')]
    answer_key_files = {}
    if os.path.exists(ANSWER_KEYS_FOLDER):
        for f in os.listdir(ANSWER_KEYS_FOLDER):
            if f.lower().endswith('.pdf'):
                base_name = f.replace(' (Answer Key)', '')
                answer_key_files[base_name] = f
    return render_template('index.html', exam_files=exam_files, answer_key_files=answer_key_files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(EXAMS_FOLDER, filename)

@app.route('/download_key/<filename>')
def download_key(filename):
    return send_from_directory(ANSWER_KEYS_FOLDER, filename)

@app.route('/tutors')
def tutors():
    return render_template('tutors.html')

@app.route('/become_tutor', methods=['GET', 'POST'])
def become_tutor():
    # existing become_tutor logic
    # ...
    return render_template('become_tutor.html')

# New route: Upload past exams
@app.route('/upload_exams', methods=['GET', 'POST'])
def upload_exams():
    if request.method == 'POST':
        pdf = request.files.get('exam_pdf')
        if not pdf or not pdf.filename.lower().endswith('.pdf'):
            flash('Please upload a valid PDF file.', 'error')
            return redirect(url_for('upload_exams'))
        # Send email notification
        msg = Message(
            subject='New exam uploaded',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]
        )
        msg.body = f"User uploaded: {pdf.filename}"
        msg.attach(pdf.filename, pdf.mimetype, pdf.read())
        mail.send(msg)
        flash('Thank you! Your file has been sent to the team.', 'success')
        return redirect(url_for('index'))
    return render_template('upload_exams.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    enhanced_prompt = f"Answer the following exam-related question with detailed explanations: {query}"
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': enhanced_prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        answer = response.choices[0].message['content'].strip()
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tutors', methods=['GET'])
def api_tutors():
    tutors = TutorApplication.query.all()
    tutor_list = []
    for tutor in tutors:
        tutor_list.append({
            'id': tutor.id,
            'name': tutor.name,
            'location': tutor.location,
            'school': tutor.school,
            'hourly_rate': tutor.hourly_rate,
            'experience': tutor.experience,
            'classes_taught': tutor.classes_taught,
            'phone': tutor.phone,
            'email': tutor.email,
            'cv_bio': tutor.cv_bio,
            'profile_bio': tutor.profile_bio
        })
    return jsonify(tutor_list)

@app.route('/answer_keys')
def answer_keys_page():
    answer_keys = []
    if os.path.exists(ANSWER_KEYS_FOLDER):
        answer_keys = [f for f in os.listdir(ANSWER_KEYS_FOLDER) if f.lower().endswith('.pdf')]
    return render_template('answer_keys.html', keys=answer_keys)

if __name__ == '__main__':
    app.run(debug=True)