"""
routes/history.py
History page: filterable monitoring history table + charts, and
CSV/"Excel" export (PDF export stub — see the /history/export/pdf route).
"""

import csv
import io
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user

from models.sensor import SensorReading
from models.misting import MistingEvent

history_bp = Blueprint("history", __name__)

FILTER_WINDOWS = {
    "today": timedelta(days=1),
    "week": timedelta(days=7),
    "month": timedelta(days=30),
    "year": timedelta(days=365),
}


def _filtered_readings(period: str):
    window = FILTER_WINDOWS.get(period, FILTER_WINDOWS["week"])
    since = datetime.utcnow() - window
    return (
        SensorReading.query.filter(
            SensorReading.user_id == current_user.id, SensorReading.recorded_at >= since
        )
        .order_by(SensorReading.recorded_at.desc())
        .all()
    )


@history_bp.route("/history")
@login_required
def index():
    period = request.args.get("period", "week")
    if period not in FILTER_WINDOWS:
        period = "week"

    readings = _filtered_readings(period)
    chart_source = list(reversed(readings))[-60:]

    return render_template(
        "history.html",
        period=period,
        readings=readings[:100],
        chart_labels=[r.recorded_at.strftime("%d/%m %H:%M") for r in chart_source],
        chart_temp=[r.indoor_temp_c for r in chart_source],
        chart_humidity=[r.indoor_humidity_pct for r in chart_source],
        chart_health=[r.bee_health_score for r in chart_source],
        misting_events_count=len(
            [e for e in MistingEvent.query.filter_by(user_id=current_user.id).all()
             if e.started_at >= datetime.utcnow() - FILTER_WINDOWS[period]]
        ),
    )


@history_bp.route("/history/export/csv")
@login_required
def export_csv():
    readings = _filtered_readings(request.args.get("period", "week"))

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "Date", "Indoor Temp (C)", "Outdoor Temp (C)", "Humidity (%)",
        "Bee Health", "Heat Stress Risk (%)", "Colony Status",
    ])
    for r in readings:
        writer.writerow([
            r.recorded_at.strftime("%Y-%m-%d %H:%M"), r.indoor_temp_c, r.outdoor_temp_c,
            r.indoor_humidity_pct, r.bee_health_score, r.heat_stress_risk_pct, r.colony_status,
        ])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=selamet_history.csv"},
    )


@history_bp.route("/history/export/pdf")
@login_required
def export_pdf():
    # TODO: render a proper PDF report (e.g. with WeasyPrint or ReportLab).
    # Returning CSV data for now keeps the "Export" action functional end-to-end.
    return export_csv()
