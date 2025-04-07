import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import configuration from config.py
import openai  # For the AI assistant endpoint (if used)
from werkzeug.utils import secure_filename  # For safely handling file names

app = Flask(__name__)
app.config.from_object(Config)

# Set secret key for session/flash
app.secret_key = "ignz upkj myar isiz"

# Configure Flask-Mail for Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tzstudies2024@gmail.com'
app.config['MAIL_PASSWORD'] = 'ignz upkj myar isiz'  # Your 16-char App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Tutor Application', 'tzstudies2024@gmail.com')
mail = Mail(app)

# Initialize SQLAlchemy with PostgreSQL connection from config.py
db = SQLAlchemy(app)

# Define the TutorApplication model with the CV now storing the file path
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
    cv_bio = db.Column(db.Text, nullable=False)          # Now stores the file path of the CV
    profile_bio = db.Column(db.Text, nullable=False)       # Public profile description

with app.app_context():
    db.create_all()

# Define folder paths for exam PDFs and answer key PDFs (if used)
EXAMS_FOLDER = os.path.join(os.getcwd(), "exams")
ANSWER_KEYS_FOLDER = os.path.join(os.getcwd(), "answer_keys")

# Define folder for CV uploads
CV_UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "cvs")
if not os.path.exists(CV_UPLOAD_FOLDER):
    os.makedirs(CV_UPLOAD_FOLDER)

@app.route('/')
def index():
    # List all PDF files in the exams folder
    exam_files = [f for f in os.listdir(EXAMS_FOLDER) if f.lower().endswith('.pdf')]
    
    # Optionally, list answer key PDFs if available
    answer_key_files = {}
    if os.path.exists(ANSWER_KEYS_FOLDER):
        for f in os.listdir(ANSWER_KEYS_FOLDER):
            if f.lower().endswith('.pdf'):
                base_name = f.replace(" (Answer Key)", "")
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
    # Render a static tutors page
    return render_template('tutors.html')

@app.route('/become_tutor', methods=['GET', 'POST'])
def become_tutor():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        school = request.form.get('school', '').strip()
        hourly_rate = request.form.get('hourly_rate', '').strip()
        experience = request.form.get('experience', '').strip()
        classes_taught = request.form.get('classes_taught', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        # Get the uploaded CV file
        cv_file = request.files.get('cv_file')
        profile_bio = request.form.get('profile_bio', '').strip()   # Public profile bio field

        # Validate required fields (phone is optional)
        if (not name or not location or not school or not hourly_rate or
            not experience or not classes_taught or not email or not cv_file or not profile_bio):
            error = "Please fill in all required fields and upload your CV."
            return render_template('become_tutor.html', error=error)
        
        # Save the uploaded CV file
        filename = secure_filename(cv_file.filename)
        file_path = os.path.join(CV_UPLOAD_FOLDER, filename)
        cv_file.save(file_path)
        
        # Prepare email content for admin notification without showing the file path
        subject = "New Tutor Application"
        body = f"""
New Tutor Application:

Name: {name}
Location: {location}
School/Institution: {school}
Hourly Rate: {hourly_rate}
Experience: {experience}
Classes Taught: {classes_taught}
Phone: {phone}
Email: {email}

Profile Bio:
{profile_bio}
        """
        try:
            msg = Message(subject=subject, recipients=["tzstudies2024@gmail.com"], body=body)
            # Attach the uploaded CV file to the email
            with open(file_path, 'rb') as fp:
                file_data = fp.read()
            msg.attach(filename, cv_file.content_type, file_data)
            mail.send(msg)
        except Exception as e:
            error = f"An error occurred while sending your application: {str(e)}"
            return render_template('become_tutor.html', error=error)
        
        # Insert the application into the PostgreSQL database
        new_application = TutorApplication(
            name=name,
            location=location,
            school=school,
            hourly_rate=hourly_rate,
            experience=experience,
            classes_taught=classes_taught,
            phone=phone,
            email=email,
            cv_bio=file_path,  # Save the file path in the database
            profile_bio=profile_bio
        )
        db.session.add(new_application)
        db.session.commit()
        
        # Send a confirmation email to the tutor if an email was provided
        if email:
            try:
                confirmation_subject = "We Received Your Tutor Application"
                confirmation_html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: auto; border: 1px solid #e0e0e0; padding: 20px;">
                      <div style="text-align: center;">
                        <img src="https://tzstudies-a4167b41d2dd.herokuapp.com/static/tutors/tzstudies.png" alt="TZStudies Logo" style="max-width: 200px;"/>
                      </div>
                      <h2 style="color: #1d3557;">We Received Your Tutor Application</h2>
                      <p>Hello {name},</p>
                      <p>Thank you for applying to become a tutor with TZStudies. We have received your application, and due to a high volume of candidates, please allow 7–10 business days for an update regarding your application status.</p>
                      <p>If you have any questions, please feel free to contact us at <a href="mailto:tzstudies2024@gmail.com">tzstudies2024@gmail.com</a>.</p>
                      <p>In the meantime, we invite you to explore our YouTube channel for educational resources and updates:</p>
                      <div style="text-align: center; margin: 20px;">
                        <a href="https://www.youtube.com/@TZStudies-uh9zh" style="background-color: #1d3557; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Visit Our YouTube Channel</a>
                      </div>
                      <p>Thank you once again for your interest.</p>
                      <p>Best regards,<br>TZStudies</p>
                    </div>
                  </body>
                </html>
                """
                confirmation_msg = Message(subject=confirmation_subject, recipients=[email], html=confirmation_html)
                mail.send(confirmation_msg)
            except Exception as e:
                print(f"Error sending confirmation email: {e}")
        
        success = "Your application has been submitted successfully!"
        return render_template('become_tutor.html', success=success)
    
    return render_template('become_tutor.html')

# ---------------- AI Assistant Endpoint ----------------

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    enhanced_prompt = f"Answer the following exam-related question with detailed explanations: {query}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": enhanced_prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        answer = response.choices[0].message["content"].strip()
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- REST API Endpoint ----------------

@app.route('/api/tutors', methods=['GET'])
def api_tutors():
    tutors = TutorApplication.query.all()
    tutor_list = []
    for tutor in tutors:
        tutor_list.append({
            "id": tutor.id,
            "name": tutor.name,
            "location": tutor.location,
            "school": tutor.school,
            "hourly_rate": tutor.hourly_rate,
            "experience": tutor.experience,
            "classes_taught": tutor.classes_taught,
            "phone": tutor.phone,
            "email": tutor.email,
            "cv_bio": tutor.cv_bio,
            "profile_bio": tutor.profile_bio
        })
    return jsonify(tutor_list)

@app.route('/answer_keys')
def answer_keys_page():
    answer_keys = []
    if os.path.exists(ANSWER_KEYS_FOLDER):
        answer_keys = [f for f in os.listdir(ANSWER_KEYS_FOLDER) if f.lower().endswith('.pdf')]
    return render_template('answer_keys.html', keys=answer_keys)

