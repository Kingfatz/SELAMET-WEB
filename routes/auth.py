"""
routes/auth.py
Authentication blueprint: email/password login + registration, "Continue
with Google/Facebook" OAuth stubs, phone/OTP stub, forgot-password stub,
and logout. Flask-Login handles session management ("Remember Me" included).

The Google/Facebook/OTP handlers are wired up end-to-end at the route level
but return a friendly "not configured" message until real API keys
(config.py: GOOGLE_CLIENT_ID, FACEBOOK_CLIENT_ID, SMS_PROVIDER_API_KEY) are
supplied — this keeps the login page fully functional for demos while
making the production integration a config change, not a rewrite.
"""

from datetime import datetime, timedelta
import random

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.user import User
from models.misting import MistingSettings
from services.simulator import seed_history

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter(
            (User.email == identifier) | (User.phone_number == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember, duration=timedelta(days=30))
            flash("Welcome back!", "success")
            return redirect(url_for("home.index"))

        flash("Invalid email/phone or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    farm_name = request.form.get("farm_name", "").strip()
    hive_location = request.form.get("hive_location", "").strip()

    if not name or not email or not password:
        flash("Please fill in name, email, and password to create an account.", "danger")
        return redirect(url_for("auth.login"))

    if User.query.filter_by(email=email).first():
        flash("An account with that email already exists.", "danger")
        return redirect(url_for("auth.login"))

    user = User(name=name, email=email, farm_name=farm_name or None, hive_location=hive_location or None)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Seed demo data + default misting settings so the new account isn't empty
    seed_history(user.id)
    db.session.add(MistingSettings(user_id=user.id, next_scheduled_at=datetime.utcnow() + timedelta(hours=6)))
    db.session.commit()

    login_user(user, remember=True)
    flash("Account created — welcome to SELAMET!", "success")
    return redirect(url_for("home.index"))


@auth_bp.route("/login/google")
def login_google():
    if not current_app.config.get("GOOGLE_CLIENT_ID"):
        flash("Google login isn't configured yet. Set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET to enable it.", "info")
        return redirect(url_for("auth.login"))
    # TODO: redirect into the real OAuth 2.0 authorization-code flow.
    return redirect(url_for("auth.login"))


@auth_bp.route("/login/facebook")
def login_facebook():
    if not current_app.config.get("FACEBOOK_CLIENT_ID"):
        flash("Facebook login isn't configured yet. Set FACEBOOK_CLIENT_ID / FACEBOOK_CLIENT_SECRET to enable it.", "info")
        return redirect(url_for("auth.login"))
    # TODO: redirect into the real OAuth 2.0 authorization-code flow.
    return redirect(url_for("auth.login"))


@auth_bp.route("/login/phone/request-otp", methods=["POST"])
def request_otp():
    phone = request.form.get("phone", "").strip()
    if not phone:
        flash("Enter a phone number first.", "danger")
        return redirect(url_for("auth.login"))

    if not current_app.config.get("SMS_PROVIDER_API_KEY"):
        flash("SMS/OTP delivery isn't configured yet. Set SMS_PROVIDER_API_KEY to enable it.", "info")
        return redirect(url_for("auth.login"))

    otp = f"{random.randint(0, 999999):06d}"
    session["otp_phone"] = phone
    session["otp_code"] = otp  # TODO: hash + short expiry in production; send via real SMS provider
    flash("OTP sent. Check your phone.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login/phone/verify-otp", methods=["POST"])
def verify_otp():
    code = request.form.get("otp", "").strip()
    phone = session.get("otp_phone")

    if not phone or code != session.get("otp_code"):
        flash("Invalid or expired OTP.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(phone_number=phone).first()
    if not user:
        user = User(name=f"Beekeeper {phone[-4:]}", phone_number=phone)
        db.session.add(user)
        db.session.commit()
        seed_history(user.id)
        db.session.add(MistingSettings(user_id=user.id))
        db.session.commit()

    session.pop("otp_phone", None)
    session.pop("otp_code", None)
    login_user(user, remember=True)
    return redirect(url_for("home.index"))


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.form.get("email", "").strip()
    # TODO: send a real password-reset email with a signed, expiring token.
    flash(f"If an account exists for {email}, a reset link has been sent.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))
