"""
routes/home.py
Home dashboard: KPI cards, health score, microclimate status, risk cards,
environmental monitoring grid, honey production estimate, smart misting
summary, live camera preview, 24h activity chart, and recent notifications.
"""

from datetime import datetime, timedelta

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.sensor import SensorReading
from models.notification import Notification
from models.misting import MistingSettings, MistingEvent
from models.weather import WeatherRecord
from models.camera_info import CameraInfo
from services.simulator import latest_honey_yield_kg

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
@home_bp.route("/home")
@login_required
def index():
    latest = (
        SensorReading.query.filter_by(user_id=current_user.id)
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )

    since = datetime.utcnow() - timedelta(hours=24)
    last_24h = (
        SensorReading.query.filter(
            SensorReading.user_id == current_user.id, SensorReading.recorded_at >= since
        )
        .order_by(SensorReading.recorded_at.asc())
        .all()
    )

    # Colony counts across the last 24h window (demo proxy for per-hive status)
    healthy = sum(1 for r in last_24h if r.colony_status == "healthy")
    warning = sum(1 for r in last_24h if r.colony_status == "warning")
    critical = sum(1 for r in last_24h if r.colony_status == "critical")
    total = max(1, len(last_24h))

    misting = MistingSettings.query.filter_by(user_id=current_user.id).first()
    last_event = (
        MistingEvent.query.filter_by(user_id=current_user.id)
        .order_by(MistingEvent.started_at.desc())
        .first()
    )
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    activations_today = MistingEvent.query.filter(
        MistingEvent.user_id == current_user.id, MistingEvent.started_at >= today_start
    ).count()

    weather = (
        WeatherRecord.query.filter_by(user_id=current_user.id)
        .order_by(WeatherRecord.recorded_at.desc())
        .first()
    )

    cam = CameraInfo.query.filter_by(user_id=current_user.id).first()

    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(6)
        .all()
    )

    chart_labels = [r.recorded_at.strftime("%H:%M") for r in last_24h[-24:]]
    chart_temp = [r.indoor_temp_c for r in last_24h[-24:]]
    chart_humidity = [r.indoor_humidity_pct for r in last_24h[-24:]]
    chart_health = [r.bee_health_score for r in last_24h[-24:]]
    chart_outdoor_temp = [r.outdoor_temp_c for r in last_24h[-24:]]
    chart_outdoor_humidity = [r.outdoor_humidity_pct for r in last_24h[-24:]]

    honey_kg = latest_honey_yield_kg(latest.bee_health_score if latest else 75)

    return render_template(
        "home.html",
        latest=latest,
        healthy_pct=round(healthy / total * 100),
        warning_pct=round(warning / total * 100),
        critical_pct=round(critical / total * 100),
        healthy_count=max(1, round(healthy / total * 12)),
        warning_count=round(warning / total * 12),
        critical_count=round(critical / total * 12),
        misting=misting,
        last_event=last_event,
        activations_today=activations_today,
        weather=weather,
        cam=cam,
        notifications=notifications,
        chart_labels=chart_labels,
        chart_temp=chart_temp,
        chart_humidity=chart_humidity,
        chart_health=chart_health,
        chart_outdoor_temp=chart_outdoor_temp,
        chart_outdoor_humidity=chart_outdoor_humidity,
        honey_kg=honey_kg,
        now=datetime.now(),
    )
