"""
models/misting.py
Two models for the Smart Misting feature:
- MistingSettings: one row per user, the current configuration/state.
- MistingEvent: append-only log of every activation (manual or automatic).
"""

from datetime import datetime
from models import db


class MistingSettings(db.Model):
    __tablename__ = "misting_settings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    is_on = db.Column(db.Boolean, default=False)
    mode = db.Column(db.String(10), default="automatic")   # 'automatic' | 'manual'

    trigger_temp_c = db.Column(db.Float, default=36.0)
    trigger_humidity_pct = db.Column(db.Float, default=35.0)

    duration_seconds = db.Column(db.Integer, default=30)
    relay_delay_ms = db.Column(db.Integer, default=500)

    water_tank_pct = db.Column(db.Float, default=82.0)
    pump_health_pct = db.Column(db.Float, default=97.0)
    relay_status = db.Column(db.String(20), default="ready")  # ready | active | fault

    next_scheduled_at = db.Column(db.DateTime, nullable=True)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MistingEvent(db.Model):
    __tablename__ = "misting_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    triggered_by = db.Column(db.String(10), default="auto")   # 'auto' | 'manual' | 'emergency_stop'
    duration_seconds = db.Column(db.Integer)
    trigger_temp_c = db.Column(db.Float, nullable=True)
    trigger_humidity_pct = db.Column(db.Float, nullable=True)

    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
