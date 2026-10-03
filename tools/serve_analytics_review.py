"""Isolated browser-check server. Never connects to or promotes users in the real database."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = "sqlite:///analytics-review.db"

from tzstudies import create_app  # noqa: E402
from tzstudies.config import DevelopmentConfig  # noqa: E402
from tzstudies.extensions import db  # noqa: E402
from tzstudies.models import User  # noqa: E402
from tzstudies.security import hash_password  # noqa: E402

DevelopmentConfig.RATELIMIT_ENABLED = False
app = create_app("development")
app.config.update(MAIL_SUPPRESS_SEND=True, MAIL_USERNAME="", OPENAI_API_KEY="", RATELIMIT_ENABLED=False)
app.extensions["mail"].suppress = True
with app.app_context():
    expected = (ROOT / "instance" / "analytics-review.db").resolve()
    if Path(db.engine.url.database).resolve() != expected:
        raise RuntimeError("Review database must be the isolated workspace fixture.")
    if "--reset" in sys.argv:
        db.drop_all()
        db.create_all()
    if not User.query.filter_by(email="admin@example.test").first():
        db.session.add(User(name="Review admin", email="admin@example.test", pw_hash=hash_password("River stones remember sunrise!"), is_admin=True))
        db.session.commit()
app.run(port=5051, debug=False)
