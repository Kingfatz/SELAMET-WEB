# SELAMET
**S**mart **E**co-climate & **L**ocal **A**piculture **M**icroclimate **E**nhancement **T**echnology

An IoT-based precision beekeeping dashboard — Python/Flask backend, vanilla HTML/CSS/JS
frontend (Bootstrap 5 + Chart.js), SQLite database, real-time updates via Flask-SocketIO.

This build is fully functional end-to-end: register an account, log in, and every page
(Home, Prediction, History, Live Camera, Smart Misting, Settings) works against real
database-backed data. Live sensor/AI data is currently **simulated** (see "Where real
hardware plugs in" below) so the dashboard is demo-ready without any physical ESP32 setup.

## Quick start

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** — you'll land on the login page. Click **Create Account**
to register (email + password); the app auto-seeds 14 days of realistic sensor history,
notifications, and default misting settings so the dashboard isn't empty on first login.

A background thread pushes a new simulated sensor reading every 1 minute over
Socket.IO, so the Home page's health score / temperature / humidity update live without
refreshing. Set `SELAMET_SIMULATE=false` before running to disable this if you only want
manually-seeded historical data.

## Project structure

```
SELAMET/
├── app.py                 # App factory, SocketIO, background simulator loop
├── config.py               # Env-driven config (DB, secrets, OAuth/SMS/weather keys)
├── requirements.txt
├── database/                # SQLite file lives here (selamet.db, created on first run)
├── models/                  # SQLAlchemy models (user, sensor, prediction, misting, camera, notification, weather)
├── routes/                  # Flask Blueprints — one file per page/feature
├── services/                 # simulator.py (mock sensors), prediction_service.py (forecast engine)
├── utils/                   # Shared Jinja helpers (status badges, "x min ago", etc.)
├── ai/inference.py           # Placeholder — wire up YOLOv8n/TFLite here
├── camera/stream_manager.py  # Placeholder — RTSP/MJPEG bridging goes here
├── iot/esp32_client.py       # Placeholder — real ESP32 REST/MQTT integration goes here
├── static/{css,js,icons,images,uploads}/
└── templates/                # layout.html (shell) + one template per page
```

## Where real hardware/services plug in

Everything below is stubbed with clear `TODO`s so swapping in real integrations doesn't
require touching templates or the database schema:

| Feature | Stub location | What to do |
|---|---|---|
| ESP32 sensors / relay | `iot/esp32_client.py` | Implement `fetch_latest_reading()` / `send_relay_command()` (HTTP or MQTT), then call from `routes/api.py` / `routes/misting.py` instead of `services/simulator.py` |
| ESP32-CAM / RTSP stream | `camera/stream_manager.py` | Implement `get_stream_url()`; for RTSP, proxy to MJPEG/HLS since browsers can't play RTSP directly |
| Bee detection / health ML | `ai/inference.py` | Drop in a YOLOv8n/YOLOv11n + TensorFlow Lite pipeline; today `services/prediction_service.py` uses a transparent rule engine as a placeholder |
| Google / Facebook login | `routes/auth.py` (`login_google`, `login_facebook`) | Set `GOOGLE_CLIENT_ID`/`SECRET`, `FACEBOOK_CLIENT_ID`/`SECRET` env vars and complete the OAuth 2.0 authorization-code flow |
| Phone/OTP login | `routes/auth.py` (`request_otp`, `verify_otp`) | Set `SMS_PROVIDER_API_KEY` and call your SMS provider instead of the in-session demo code |
| Weather | `models/weather.py`, config `OPENWEATHER_API_KEY` / `BMKG_API_BASE` | Add a `services/weather_service.py` that fetches + caches into `WeatherRecord` on a schedule |
| PDF export | `routes/history.py` (`export_pdf`) | Currently aliases to CSV export; swap in WeasyPrint/ReportLab for a real PDF report |

## Notes

- **Dark mode** is per-user (`User.theme`) and applied via `data-theme` on `<html>`.
- **PWA-ready**: `static/manifest.webmanifest` is wired up; add real icon PNGs under
  `static/icons/` (192×192 and 512×512) to finish installability.
- Passwords are hashed with Werkzeug's `generate_password_hash` — never stored in plaintext.
- For production, run behind a real WSGI/ASGI server (e.g. `gunicorn -k eventlet` or
  `daphne`) instead of `python app.py`, and set a strong `SELAMET_SECRET_KEY`.
