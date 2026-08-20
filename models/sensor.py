"""
models/sensor.py
Time-series sensor readings coming from ESP32 nodes (or the simulator while
real hardware is not yet connected). One row = one snapshot in time for a
given hive/apiary.
"""

from datetime import datetime
from models import db


class SensorReading(db.Model):
    __tablename__ = "sensor_readings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    hive_id = db.Column(db.String(50), default="hive-01")

    # Environment
    indoor_temp_c = db.Column(db.Float)
    outdoor_temp_c = db.Column(db.Float)
    indoor_humidity_pct = db.Column(db.Float)
    outdoor_humidity_pct = db.Column(db.Float)
    light_intensity_lux = db.Column(db.Float)
    wind_speed_ms = db.Column(db.Float)
    rain_probability_pct = db.Column(db.Float)

    # Colony health
    bee_health_score = db.Column(db.Float)          # 0-100
    colony_status = db.Column(db.String(20))         # healthy | warning | critical
    heat_stress_risk_pct = db.Column(db.Float)
    food_deficiency_risk_pct = db.Column(db.Float)
    absconding_risk_pct = db.Column(db.Float)
    swarming_risk_pct = db.Column(db.Float)

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SensorReading hive={self.hive_id} at={self.recorded_at}>"
