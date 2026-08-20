"""
routes/prediction.py
Prediction page: horizon selector (7/14/30 days), forecast KPI cards,
forecast timeline chart data, flowering calendar, and weather forecast.
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models.prediction import Prediction
from services.prediction_service import generate_forecast, FLOWERING_CALENDAR

prediction_bp = Blueprint("prediction", __name__)


@prediction_bp.route("/prediction")
@login_required
def index():
    horizon = request.args.get("horizon", default=7, type=int)
    if horizon not in (7, 14, 30):
        horizon = 7

    existing = (
        Prediction.query.filter_by(user_id=current_user.id, horizon_days=horizon)
        .order_by(Prediction.target_date)
        .all()
    )
    forecasts = existing if existing else generate_forecast(current_user.id, horizon)

    next_forecast = forecasts[0] if forecasts else None

    return render_template(
        "prediction.html",
        horizon=horizon,
        forecasts=forecasts,
        next_forecast=next_forecast,
        flowering_calendar=FLOWERING_CALENDAR,
        chart_labels=[f.target_date.strftime("%d %b") for f in forecasts],
        chart_health=[f.predicted_bee_health_score for f in forecasts],
        chart_heat_stress=[f.predicted_heat_stress_risk_pct for f in forecasts],
        chart_absconding=[f.predicted_absconding_risk_pct for f in forecasts],
        chart_temp=[f.predicted_temp_c for f in forecasts],
        chart_humidity=[f.predicted_humidity_pct for f in forecasts],
        chart_rain=[f.predicted_rain_probability_pct for f in forecasts],
        chart_honey=[f.predicted_honey_production_kg for f in forecasts],
    )


@prediction_bp.route("/prediction/refresh", methods=["POST"])
@login_required
def refresh():
    horizon = request.form.get("horizon", default=7, type=int)
    generate_forecast(current_user.id, horizon)
    from flask import redirect, url_for
    return redirect(url_for("prediction.index", horizon=horizon))
