"""
models/weather.py
Cached weather snapshots so we don't call OpenWeather/BMKG on every page
load. services/weather_service.py refreshes this on a schedule.
"""

from datetime import datetime
from models import db


class WeatherRecord(db.Model):
    __tablename__ = "weather_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    location_name = db.Column(db.String(120), default="")
    temp_c = db.Column(db.Float)
    humidity_pct = db.Column(db.Float)
    rain_probability_pct = db.Column(db.Float)
    wind_speed_ms = db.Column(db.Float)
    condition = db.Column(db.String(40), default="clear")   # clear | cloudy | rain | storm
    source = db.Column(db.String(20), default="simulated")  # openweather | bmkg | simulated

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
