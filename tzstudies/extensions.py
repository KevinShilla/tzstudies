"""Shared Flask extension instances.

Created here (without an app) so that blueprints can import them
without causing circular imports.  They are initialised with the
app inside ``create_app()``.
"""

from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from tzstudies.secure_mail import SecureMail

db = SQLAlchemy()
mail = SecureMail()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])
cache = Cache()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
