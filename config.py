"""
config.py
Central configuration for the SELAMET Flask application.
Reads sensitive values from environment variables with safe local defaults
so the project runs out-of-the-box for demos/judging.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core Flask ---
    SECRET_KEY = os.environ.get("SELAMET_SECRET_KEY", "selamet-dev-secret-change-me")

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SELAMET_DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'selamet.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Sessions / Auth ---
    REMEMBER_COOKIE_DURATION_DAYS = 30
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # --- OAuth placeholders (fill in for production) ---
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID", "")
    FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET", "")

    # --- OTP / SMS provider placeholder ---
    SMS_PROVIDER_API_KEY = os.environ.get("SMS_PROVIDER_API_KEY", "")

    # --- Weather API placeholders ---
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
    BMKG_API_BASE = os.environ.get("BMKG_API_BASE", "")

    # --- IoT / Camera ---
    ESP32_CAM_DEFAULT_URL = os.environ.get("ESP32_CAM_DEFAULT_URL", "")
    MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "")
    MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))

    # --- Simulation mode (True until real ESP32 hardware is wired up) ---
    SIMULATE_SENSORS = os.environ.get("SELAMET_SIMULATE", "true").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
