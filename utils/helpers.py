"""
utils/helpers.py
Small reusable helpers shared across route blueprints and templates.
"""

from datetime import datetime


def status_badge_class(status: str) -> str:
    """Map a colony/camera/misting status string to a CSS badge class."""
    mapping = {
        "healthy": "badge-healthy",
        "online": "badge-healthy",
        "ready": "badge-healthy",
        "warning": "badge-warning",
        "critical": "badge-critical",
        "fault": "badge-critical",
        "offline": "badge-critical",
        "info": "badge-info",
    }
    return mapping.get((status or "").lower(), "badge-info")


def human_time_ago(dt: datetime) -> str:
    """Render a datetime as '5 min ago' / '2 hr ago' style text."""
    if not dt:
        return "—"
    delta = datetime.utcnow() - dt
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"
    days = hours // 24
    return f"{days} day(s) ago"


def register_template_helpers(app):
    """Expose helpers to Jinja templates without importing them in every view."""
    app.jinja_env.globals.update(
        status_badge_class=status_badge_class,
        human_time_ago=human_time_ago,
        getattr=getattr,  # lets templates do getattr(current_user, 'notify_email') etc.
    )
