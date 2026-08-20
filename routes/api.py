"""
routes/api.py
REST API blueprint consumed by static/js/main.js via fetch() for real-time-ish
polling, and mirrored over Flask-SocketIO (see app.py's background thread)
for true push updates. This is the seam where real ESP32/MQTT data would
replace services/simulator.py's generated readings.
"""

from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from models.sensor import SensorReading
from models.misting import MistingSettings
from models.notification import Notification

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/latest-reading")
@login_required
def latest_reading():
    r = (
        SensorReading.query.filter_by(user_id=current_user.id)
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )
    if not r:
        return jsonify({"error": "no data yet"}), 404

    return jsonify(
        {
            "indoor_temp_c": r.indoor_temp_c,
            "outdoor_temp_c": r.outdoor_temp_c,
            "indoor_humidity_pct": r.indoor_humidity_pct,
            "outdoor_humidity_pct": r.outdoor_humidity_pct,
            "bee_health_score": r.bee_health_score,
            "colony_status": r.colony_status,
            "heat_stress_risk_pct": r.heat_stress_risk_pct,
            "food_deficiency_risk_pct": r.food_deficiency_risk_pct,
            "absconding_risk_pct": r.absconding_risk_pct,
            "swarming_risk_pct": r.swarming_risk_pct,
            "recorded_at": r.recorded_at.isoformat(),
        }
    )


@api_bp.route("/misting-status")
@login_required
def misting_status():
    s = MistingSettings.query.filter_by(user_id=current_user.id).first()
    if not s:
        return jsonify({"error": "not configured"}), 404
    return jsonify(
        {
            "is_on": s.is_on,
            "mode": s.mode,
            "water_tank_pct": s.water_tank_pct,
            "pump_health_pct": s.pump_health_pct,
            "relay_status": s.relay_status,
        }
    )


@api_bp.route("/notifications/unread-count")
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({"unread": count})
