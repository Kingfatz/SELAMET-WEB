"""
routes/misting.py
Smart Misting page + controls: status card, ON/OFF/emergency-stop,
automatic/manual mode, timer/threshold config, water tank & pump health,
and history chart. Real relay commands go through iot/esp32_client.py once
hardware is connected — today actions just update MistingSettings /
MistingEvent and (optionally) emit a SocketIO event for real-time UI updates.
"""

from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.misting import MistingSettings, MistingEvent

misting_bp = Blueprint("misting", __name__)


def _get_or_create_settings():
    settings = MistingSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = MistingSettings(user_id=current_user.id, next_scheduled_at=datetime.utcnow() + timedelta(hours=4))
        db.session.add(settings)
        db.session.commit()
    return settings


@misting_bp.route("/misting")
@login_required
def index():
    settings = _get_or_create_settings()
    events = (
        MistingEvent.query.filter_by(user_id=current_user.id)
        .order_by(MistingEvent.started_at.desc())
        .limit(20)
        .all()
    )
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    activations_today = MistingEvent.query.filter(
        MistingEvent.user_id == current_user.id, MistingEvent.started_at >= today_start
    ).count()

    all_events = MistingEvent.query.filter_by(user_id=current_user.id).all()
    trigger_counts = {
        "manual": sum(1 for e in all_events if e.triggered_by == "manual"),
        "auto": sum(1 for e in all_events if e.triggered_by == "auto"),
        "emergency_stop": sum(1 for e in all_events if e.triggered_by == "emergency_stop"),
    }

    chart_source = list(reversed(events))
    return render_template(
        "misting.html",
        settings=settings,
        events=events,
        activations_today=activations_today,
        trigger_counts=trigger_counts,
        chart_labels=[e.started_at.strftime("%d/%m %H:%M") for e in chart_source],
        chart_duration=[e.duration_seconds for e in chart_source],
    )


@misting_bp.route("/misting/toggle", methods=["POST"])
@login_required
def toggle():
    settings = _get_or_create_settings()
    settings.is_on = not settings.is_on
    settings.relay_status = "active" if settings.is_on else "ready"
    db.session.commit()

    if settings.is_on:
        db.session.add(
            MistingEvent(
                user_id=current_user.id,
                triggered_by="manual",
                duration_seconds=settings.duration_seconds,
                trigger_temp_c=None,
                trigger_humidity_pct=None,
            )
        )
        db.session.commit()
        flash("Misting turned ON.", "success")
    else:
        flash("Misting turned OFF.", "info")

    return redirect(url_for("misting.index"))


@misting_bp.route("/misting/emergency-stop", methods=["POST"])
@login_required
def emergency_stop():
    settings = _get_or_create_settings()
    settings.is_on = False
    settings.relay_status = "ready"
    db.session.commit()
    db.session.add(
        MistingEvent(user_id=current_user.id, triggered_by="emergency_stop", duration_seconds=0)
    )
    db.session.commit()
    flash("Emergency stop triggered — misting halted.", "danger")
    return redirect(url_for("misting.index"))


@misting_bp.route("/misting/settings", methods=["POST"])
@login_required
def update_settings():
    settings = _get_or_create_settings()
    settings.mode = request.form.get("mode", settings.mode)
    settings.duration_seconds = request.form.get("duration_seconds", settings.duration_seconds, type=int)
    settings.trigger_temp_c = request.form.get("trigger_temp_c", settings.trigger_temp_c, type=float)
    settings.trigger_humidity_pct = request.form.get("trigger_humidity_pct", settings.trigger_humidity_pct, type=float)
    settings.relay_delay_ms = request.form.get("relay_delay_ms", settings.relay_delay_ms, type=int)
    db.session.commit()
    flash("Misting settings updated.", "success")
    return redirect(url_for("misting.index"))
