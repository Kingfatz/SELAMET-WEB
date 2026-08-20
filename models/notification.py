"""
models/notification.py
In-app / email / push / SMS notification log, shown in the Home page's
"Recent Notifications" panel and the History page's alert history.
"""

from datetime import datetime
from models import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), default="")
    category = db.Column(db.String(20), default="info")  # info | warning | critical | success
    source = db.Column(db.String(30), default="system")  # system | ai | misting | camera

    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
