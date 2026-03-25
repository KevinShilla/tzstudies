from datetime import datetime, timezone

from flask_login import UserMixin

from tzstudies.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    history = db.relationship("History", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email}>"


class Paper(db.Model):
    __tablename__ = "paper"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(200), unique=True, nullable=False)
    category = db.Column(db.String(20))   # "exam" or "key"
    grade = db.Column(db.String(10))      # e.g. "S4", "F2", "F4"

    def __repr__(self):
        return f"<Paper {self.file_name}>"


class History(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey("paper.id"), nullable=False)
    event = db.Column(db.String(10), nullable=False)  # "view" or "download"
    viewed_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    paper = db.relationship("Paper")

    def __repr__(self):
        return f"<History user={self.user_id} paper={self.paper_id} event={self.event}>"


class TutorApplication(db.Model):
    __tablename__ = "tutor_application"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(255), nullable=False)
    classes_taught = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255), nullable=False)
    cv_filename = db.Column(db.String(255))
    profile_bio = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<TutorApplication {self.name}>"


class Comment(db.Model):
    __tablename__ = "comment"

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey("paper.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"), nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", backref="comments")
    paper = db.relationship("Paper", backref="comments")
    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Comment {self.id} by user {self.user_id}>"
