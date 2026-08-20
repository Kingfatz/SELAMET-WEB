"""
services/prediction_service.py
Produces day-by-day forecasts for the Prediction page. This is a
transparent rule-based engine today so the dashboard is fully functional
without training data. Swap `generate_forecast()`'s internals for a real
TensorFlow Lite / trained regression model later — callers (routes/prediction.py)
don't need to change since the function signature and Prediction model stay the same.
"""

import math
import random
from datetime import date, timedelta

from models import db
from models.prediction import Prediction
from models.sensor import SensorReading


def _bounded(value, lo, hi):
    return max(lo, min(hi, value))


def generate_forecast(user_id: int, horizon_days: int = 7):
    """Create (or refresh) a Prediction row per day for the given horizon."""
    latest = (
        SensorReading.query.filter_by(user_id=user_id)
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )
    base_health = latest.bee_health_score if latest else 78.0
    base_temp = latest.outdoor_temp_c if latest else 28.0

    # Clear any previous forecast for this horizon so re-runs don't duplicate rows
    Prediction.query.filter_by(user_id=user_id, horizon_days=horizon_days).delete()

    today = date.today()
    forecasts = []
    drift = 0.0
    for d in range(1, horizon_days + 1):
        drift += random.uniform(-2.5, 2.0)
        health = _bounded(base_health + drift * 0.6 + math.sin(d / 3) * 3, 30, 98)
        temp = _bounded(base_temp + math.sin(d / 4) * 3 + random.uniform(-1, 1), 20, 39)
        rain_prob = _bounded(30 + math.sin(d / 5) * 25 + random.uniform(-5, 5), 0, 100)
        heat_stress = _bounded((temp - 31) * 11 + random.uniform(-4, 4), 0, 100)
        nectar = _bounded(70 - rain_prob * 0.3 + random.uniform(-5, 5), 5, 100)
        food_deficiency = _bounded(100 - nectar + random.uniform(-5, 5), 0, 100)
        absconding = _bounded(heat_stress * 0.35 + food_deficiency * 0.25, 0, 100)
        honey_kg = _bounded(6 + (health - 50) / 50 * 4 - rain_prob / 100 * 1.5, 1.5, 13.5)

        if health >= 80 and heat_stress < 50:
            status = "healthy"
        elif health >= 55:
            status = "warning"
        else:
            status = "critical"

        forecasts.append(
            Prediction(
                user_id=user_id,
                target_date=today + timedelta(days=d),
                horizon_days=horizon_days,
                predicted_bee_health_score=round(health, 1),
                predicted_colony_status=status,
                predicted_heat_stress_risk_pct=round(heat_stress, 1),
                predicted_nectar_availability_pct=round(nectar, 1),
                predicted_honey_production_kg=round(honey_kg, 1),
                predicted_food_deficiency_risk_pct=round(food_deficiency, 1),
                predicted_absconding_risk_pct=round(absconding, 1),
                predicted_temp_c=round(temp, 1),
                predicted_humidity_pct=round(_bounded(65 - (temp - 26) * 1.5, 30, 90), 1),
                predicted_rain_probability_pct=round(rain_prob, 0),
                predicted_wind_speed_ms=round(_bounded(2.5 + random.uniform(-1, 2), 0, 10), 1),
                model_version="rule-engine-v0",
            )
        )

    db.session.bulk_save_objects(forecasts)
    db.session.commit()
    return Prediction.query.filter_by(user_id=user_id, horizon_days=horizon_days).order_by(Prediction.target_date).all()


FLOWERING_CALENDAR = [
    {"flower": "Rambutan", "bloom_pct": 78, "nectar": "High", "foraging_window": "06:00–10:00"},
    {"flower": "Kapok (Randu)", "bloom_pct": 62, "nectar": "High", "foraging_window": "05:30–09:00"},
    {"flower": "Coffee Blossom", "bloom_pct": 45, "nectar": "Medium", "foraging_window": "07:00–11:00"},
    {"flower": "Longan", "bloom_pct": 30, "nectar": "Medium", "foraging_window": "06:00–09:30"},
    {"flower": "Wildflower Mix", "bloom_pct": 55, "nectar": "Medium", "foraging_window": "All day"},
]
