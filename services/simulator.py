"""
services/simulator.py
Generates realistic-looking sensor data so the dashboard is fully demo-able
before real ESP32 hardware is wired in. Every function here is a drop-in
replacement target: once real sensors/MQTT are connected, swap the call
site (in routes/api.py) to read from iot/ instead of this module — the
rest of the app (models, templates, charts) does not need to change.
"""

import math
import random
from datetime import datetime, timedelta

from models import db
from models.sensor import SensorReading
from models.weather import WeatherRecord
from models.notification import Notification


def _bounded(value, lo, hi):
    return max(lo, min(hi, value))


def generate_reading(user_id: int, at: datetime = None) -> SensorReading:
    """Create one plausible sensor snapshot, loosely following a daily cycle."""
    at = at or datetime.utcnow()
    hour = at.hour + at.minute / 60

    # Daily temperature cycle: coolest ~4am, warmest ~2pm
    base_outdoor = 26 + 6 * math.sin((hour - 6) / 24 * 2 * math.pi)
    outdoor_temp = _bounded(base_outdoor + random.uniform(-1.2, 1.2), 18, 38)
    indoor_temp = _bounded(outdoor_temp + random.uniform(2.5, 5.5), 24, 40)

    outdoor_humidity = _bounded(75 - (outdoor_temp - 24) * 2.2 + random.uniform(-4, 4), 30, 95)
    indoor_humidity = _bounded(outdoor_humidity - random.uniform(5, 12), 25, 90)

    light = _bounded(1000 * max(0, math.sin((hour - 6) / 12 * math.pi)) + random.uniform(-50, 50), 0, 1200)
    wind = _bounded(2.5 + random.uniform(-1.5, 2.5), 0, 12)
    rain_prob = _bounded(random.uniform(0, 35) + (10 if 13 <= hour <= 17 else 0), 0, 100)

    heat_stress = _bounded((indoor_temp - 32) * 12 + random.uniform(-5, 5), 0, 100)
    food_deficiency = _bounded(random.uniform(5, 25) + (10 if rain_prob > 60 else 0), 0, 100)
    absconding = _bounded(heat_stress * 0.4 + food_deficiency * 0.2 + random.uniform(-5, 5), 0, 100)
    swarming = _bounded(random.uniform(5, 30), 0, 100)

    bee_health = _bounded(100 - (heat_stress * 0.3 + food_deficiency * 0.25 + absconding * 0.2) + random.uniform(-3, 3), 0, 100)

    if bee_health >= 80 and heat_stress < 50 and absconding < 40:
        status = "healthy"
    elif bee_health >= 55:
        status = "warning"
    else:
        status = "critical"

    reading = SensorReading(
        user_id=user_id,
        hive_id="hive-01",
        indoor_temp_c=round(indoor_temp, 1),
        outdoor_temp_c=round(outdoor_temp, 1),
        indoor_humidity_pct=round(indoor_humidity, 1),
        outdoor_humidity_pct=round(outdoor_humidity, 1),
        light_intensity_lux=round(light, 0),
        wind_speed_ms=round(wind, 1),
        rain_probability_pct=round(rain_prob, 0),
        bee_health_score=round(bee_health, 1),
        colony_status=status,
        heat_stress_risk_pct=round(heat_stress, 1),
        food_deficiency_risk_pct=round(food_deficiency, 1),
        absconding_risk_pct=round(absconding, 1),
        swarming_risk_pct=round(swarming, 1),
        recorded_at=at,
    )
    return reading


def seed_history(user_id: int, hours: int = 24 * 14):
    """Backfill sensor history so charts have data on first login."""
    now = datetime.utcnow()
    readings = []
    for h in range(hours, 0, -1):
        at = now - timedelta(hours=h)
        readings.append(generate_reading(user_id, at))
    db.session.bulk_save_objects(readings)

    weather = WeatherRecord(
        user_id=user_id,
        location_name="Local Apiary",
        temp_c=readings[-1].outdoor_temp_c,
        humidity_pct=readings[-1].outdoor_humidity_pct,
        rain_probability_pct=readings[-1].rain_probability_pct,
        wind_speed_ms=readings[-1].wind_speed_ms,
        condition="clear" if readings[-1].rain_probability_pct < 40 else "cloudy",
        source="simulated",
    )
    db.session.add(weather)

    seed_notifications = [
        Notification(user_id=user_id, title="Welcome to SELAMET", message="Your apiary dashboard is ready.", category="info", source="system"),
        Notification(user_id=user_id, title="Bee activity normal", message="Foraging activity within expected range.", category="success", source="ai"),
        Notification(user_id=user_id, title="High nectar availability", message="Flowering forecast shows strong nectar flow this week.", category="info", source="ai"),
    ]
    db.session.add_all(seed_notifications)
    db.session.commit()


def latest_honey_yield_kg(bee_health_score: float) -> float:
    """Rough weekly honey yield estimate driven by current colony health."""
    base = 6.5 + (bee_health_score - 50) / 50 * 4
    return round(_bounded(base + random.uniform(-0.6, 0.6), 1.5, 14.0), 1)
