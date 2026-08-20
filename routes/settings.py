"""
routes/settings.py
Settings page: profile (read-only farm/hive info set at signup), notification
preferences, bee-monitoring thresholds, and camera config. Appearance,
security, and smart-misting settings were moved out of this page: theme is
toggled from the topbar, and misting configuration now lives on the Misting
page itself (routes/misting.py).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.camera_info import CameraInfo
from models.misting import MistingSettings

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
@login_required
def index():
    camera = CameraInfo.query.filter_by(user_id=current_user.id).first()
    misting = MistingSettings.query.filter_by(user_id=current_user.id).first()
    return render_template("settings.html", camera=camera, misting=misting)


@settings_bp.route("/settings/profile", methods=["POST"])
@login_required
def update_profile():
    # farm_name and hive_location are intentionally NOT editable here —
    # they're captured once at account creation (see routes/auth.py).
    current_user.name = request.form.get("name", current_user.name)
    current_user.email = request.form.get("email", current_user.email)
    current_user.phone_number = request.form.get("phone_number", current_user.phone_number)
    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/notifications", methods=["POST"])
@login_required
def update_notifications():
    current_user.notify_email = bool(request.form.get("notify_email"))
    current_user.notify_push = bool(request.form.get("notify_push"))
    current_user.notify_sms = bool(request.form.get("notify_sms"))
    db.session.commit()
    flash("Notification preferences saved.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/thresholds", methods=["POST"])
@login_required
def update_thresholds():
    current_user.temp_threshold_c = request.form.get("temp_threshold_c", current_user.temp_threshold_c, type=float)
    current_user.humidity_threshold_pct = request.form.get("humidity_threshold_pct", current_user.humidity_threshold_pct, type=float)
    current_user.heat_stress_threshold = request.form.get("heat_stress_threshold", current_user.heat_stress_threshold, type=float)
    current_user.absconding_threshold = request.form.get("absconding_threshold", current_user.absconding_threshold, type=float)
    current_user.prediction_frequency_hours = request.form.get("prediction_frequency_hours", current_user.prediction_frequency_hours, type=int)
    db.session.commit()
    flash("Monitoring thresholds saved.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/camera", methods=["POST"])
@login_required
def update_camera():
    camera = CameraInfo.query.filter_by(user_id=current_user.id).first()
    if not camera:
        camera = CameraInfo(user_id=current_user.id)
        db.session.add(camera)

    camera.name = request.form.get("camera_name", camera.name)
    camera.stream_url = request.form.get("camera_url", camera.stream_url)
    camera.resolution = request.form.get("resolution", camera.resolution)
    camera.fps = request.form.get("fps", camera.fps, type=int)
    db.session.commit()
    flash("Camera settings saved.", "success")
    return redirect(url_for("settings.index"))
