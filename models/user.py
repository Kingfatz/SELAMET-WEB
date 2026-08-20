"""
models/user.py
User account model. Supports email/password, Google OAuth, Facebook OAuth,
and phone/OTP login — a user row may have a password_hash OR an oauth
provider id OR a verified phone number, depending on how they signed up.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Identity
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone_number = db.Column(db.String(32), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True)

    # OAuth
    oauth_provider = db.Column(db.String(20), nullable=True)   # 'google' | 'facebook' | None
    oauth_id = db.Column(db.String(120), nullable=True)

    # Profile
    farm_name = db.Column(db.String(120), default="")
    hive_location = db.Column(db.String(120), default="")
    avatar_url = db.Column(db.String(255), default="")

    # Notification preferences
    notify_email = db.Column(db.Boolean, default=True)
    notify_push = db.Column(db.Boolean, default=True)
    notify_sms = db.Column(db.Boolean, default=False)

    # Monitoring thresholds (used by the AI / rule engine)
    temp_threshold_c = db.Column(db.Float, default=38.0)
    humidity_threshold_pct = db.Column(db.Float, default=70.0)
    heat_stress_threshold = db.Column(db.Float, default=75.0)
    absconding_threshold = db.Column(db.Float, default=60.0)
    prediction_frequency_hours = db.Column(db.Integer, default=24)

    # Appearance
    theme = db.Column(db.String(10), default="light")   # 'light' | 'dark'
    language = db.Column(db.String(5), default="id")    # 'id' | 'en'

    # Security
    two_factor_enabled = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email or self.phone_number}>"
