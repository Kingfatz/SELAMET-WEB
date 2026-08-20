"""
app.py
SELAMET application entry point.

Wires together: SQLAlchemy models, Flask-Login auth, the modular Blueprint
routes, Jinja template helpers, and Flask-SocketIO for real-time dashboard
updates. A lightweight background thread emits a simulated sensor reading
every 1 minute over SocketIO so the Home page updates live without a
page refresh — in production, replace `_simulate_realtime_loop` with a
real MQTT subscriber / ESP32 webhook handler that emits the same event.

Run locally with:
    pip install -r requirements.txt
    python app.py
"""

import os
import threading
import time

from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

from config import config_by_name
from models import db
from utils.helpers import register_template_helpers

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access your apiary dashboard."
login_manager.login_message_category = "info"

_realtime_thread_started = False


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(env, config_by_name["development"]))

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    register_template_helpers(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Blueprints ---
    from routes.auth import auth_bp
    from routes.home import home_bp
    from routes.prediction import prediction_bp
    from routes.history import history_bp
    from routes.misting import misting_bp
    from routes.settings import settings_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(misting_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)
        db.create_all()

    _maybe_start_realtime_loop(app)

    return app


def _maybe_start_realtime_loop(app: Flask):
    """Start a single background thread that pushes simulated live readings
    over SocketIO, so the Home page's charts/KPIs update without polling.
    Guarded so the Flask reloader (which imports this module twice) doesn't
    spawn duplicate threads."""
    global _realtime_thread_started
    if _realtime_thread_started or not app.config.get("SIMULATE_SENSORS", True):
        return
    _realtime_thread_started = True

    def loop():
        from models.user import User
        from models.sensor import SensorReading
        from services.simulator import generate_reading

        with app.app_context():
            while True:
                time.sleep(60)  # 1 menit — bukan tiap detik, sesuai permintaan
                try:
                    for user in User.query.all():
                        reading = generate_reading(user.id)
                        db.session.add(reading)
                        db.session.commit()
                        socketio.emit(
                            "sensor_update",
                            {
                                "indoor_temp_c": reading.indoor_temp_c,
                                "indoor_humidity_pct": reading.indoor_humidity_pct,
                                "bee_health_score": reading.bee_health_score,
                                "colony_status": reading.colony_status,
                                "recorded_at": reading.recorded_at.isoformat(),
                            },
                            room=f"user-{user.id}",
                        )
                except Exception as exc:  # keep the loop alive across transient errors
                    print(f"[realtime loop] {exc}")

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()


@socketio.on("connect")
def handle_connect():
    from flask_login import current_user
    from flask_socketio import join_room

    if current_user.is_authenticated:
        join_room(f"user-{current_user.id}")


app = create_app()

if __name__ == "__main__":
    # allow_unsafe_werkzeug: fine for local dev/demo; front with gunicorn+eventlet
    # (or another production WSGI/ASGI server) for real deployment.
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
        allow_unsafe_werkzeug=True,
    )
