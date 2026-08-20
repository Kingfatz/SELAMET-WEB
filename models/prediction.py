"""
models/prediction.py
Stores AI/ML forecast output per day so the Prediction and History pages can
render trend charts without recomputing the model on every request.
Populated today by services/prediction_service.py (a rule-based stand-in);
swap in a real TensorFlow Lite / trained model later without changing the schema.
"""

from datetime import datetime
from models import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    target_date = db.Column(db.Date, nullable=False, index=True)
    horizon_days = db.Column(db.Integer, default=7)   # which selector run this belongs to (7/14/30)

    predicted_bee_health_score = db.Column(db.Float)
    predicted_colony_status = db.Column(db.String(20))
    predicted_heat_stress_risk_pct = db.Column(db.Float)
    predicted_nectar_availability_pct = db.Column(db.Float)
    predicted_honey_production_kg = db.Column(db.Float)
    predicted_food_deficiency_risk_pct = db.Column(db.Float)
    predicted_absconding_risk_pct = db.Column(db.Float)

    predicted_temp_c = db.Column(db.Float)
    predicted_humidity_pct = db.Column(db.Float)
    predicted_rain_probability_pct = db.Column(db.Float)
    predicted_wind_speed_ms = db.Column(db.Float)

    model_version = db.Column(db.String(30), default="rule-engine-v0")
    accuracy_pct = db.Column(db.Float, default=None)  # filled in retroactively vs actuals

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction {self.target_date} h={self.horizon_days}>"
