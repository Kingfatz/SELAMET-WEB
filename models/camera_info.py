"""
models/camera_info.py
CameraInfo: configuration for a hive-mounted camera (ESP32-CAM / IP camera / RTSP).
CameraDetection: periodic AI vision analysis results (bee counts, activity),
ready to be populated by a real YOLO/TFLite pipeline later (see /ai).
"""

from datetime import datetime
from models import db


class CameraInfo(db.Model):
    __tablename__ = "camera_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    name = db.Column(db.String(80), default="Hive Camera 1")
    stream_url = db.Column(db.String(255), default="")   # RTSP / MJPEG / ESP32-CAM URL
    stream_type = db.Column(db.String(20), default="mjpeg")  # mjpeg | rtsp | http

    resolution = db.Column(db.String(20), default="1280x720")
    fps = db.Column(db.Integer, default=15)

    status = db.Column(db.String(10), default="offline")  # online | offline
    signal_quality_pct = db.Column(db.Float, default=0.0)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CameraDetection(db.Model):
    __tablename__ = "camera_detections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    camera_id = db.Column(db.Integer, db.ForeignKey("camera_info.id"), nullable=True)

    bee_count = db.Column(db.Integer, default=0)
    flying_bees = db.Column(db.Integer, default=0)
    resting_bees = db.Column(db.Integer, default=0)
    flying_normal_bees = db.Column(db.Integer, default=0)     # lebah terbang dengan pola wajar
    flying_abnormal_bees = db.Column(db.Integer, default=0)   # lebah terbang dengan pola tidak wajar
    fanning_bees = db.Column(db.Integer, default=0)           # lebah yang sedang fanning (mengipas sarang)
    foraging_activity_pct = db.Column(db.Float, default=0.0)
    hive_entrance_traffic = db.Column(db.Integer, default=0)   # bees crossing entrance / min
    abnormal_behavior_detected = db.Column(db.Boolean, default=False)

    model_used = db.Column(db.String(30), default="placeholder")  # e.g. 'yolov8n' once wired up
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
