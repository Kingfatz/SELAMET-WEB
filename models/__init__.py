"""
models/__init__.py
Shared SQLAlchemy database instance, imported by every model module and by app.py.
Keeping `db` here (instead of inside app.py) avoids circular imports across
the modular blueprint structure.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they register with SQLAlchemy's metadata when
# `from models import db` is called during app startup / db.create_all().
from models.user import User          # noqa: E402,F401
from models.sensor import SensorReading  # noqa: E402,F401
from models.prediction import Prediction  # noqa: E402,F401
from models.misting import MistingEvent, MistingSettings  # noqa: E402,F401
from models.camera_info import CameraInfo, CameraDetection  # noqa: E402,F401
from models.notification import Notification  # noqa: E402,F401
from models.weather import WeatherRecord  # noqa: E402,F401
