
from datetime import datetime, timedelta, timezone
import secrets
import json
import urllib.request
import urllib.error

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")



def send_verification_email(email, code):
    api_key = current_app.config.get("BREVO_API_KEY")
    sender = current_app.config.get("MAIL_FROM_EMAIL")

    if not api_key or not sender:
        raise ValueError("Brevo API key or sender email is missing.")

    payload = {
        "sender": {"email": sender},
        "to": [{"email": email}],
        "subject": "Maji-Track Email Verification",
        "textContent": (
            f"Welcome to Maji-Track!\n\n"
            f"Your verification code is: {code}\n\n"
            "This code expires in 10 minutes."
        )
    }

    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            current_app.logger.info(
                "Brevo email accepted: HTTP %s",
                response.status
            )

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        current_app.logger.error(
            "Brevo API error %s: %s",
            error.code,
            error_body
        )
        raise


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({
            "error": "Username, email and password are required."
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters."
        }), 400

    existing_user = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email or username is already registered."
        }), 409

    code = f"{secrets.randbelow(1000000):06d}"

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="community_member",
        is_verified=False,
        verification_code_hash=generate_password_hash(code),
        verification_expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=10),
    )

    try:
        db.session.add(user)
        db.session.commit()

        send_verification_email(email, code)

        return jsonify({
            "message": "Registration started. Check your email for the verification code."
        }), 201

    except Exception:
        db.session.rollback()

        current_app.logger.exception("Registration failed")

        return jsonify({
            "error": "Could not complete registration. Please try again."
        }), 500


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()

    if not email or not code:
        return jsonify({
            "error": "Email and verification code are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    if user.is_verified:
        return jsonify({
            "message": "Email is already verified."
        }), 200

    if not user.verification_code_hash:
        return jsonify({
            "error": "No active verification code. Please register again or request a new code."
        }), 400

    if not check_password_hash(user.verification_code_hash, code):
        return jsonify({
            "error": "Invalid verification code."
        }), 400

    expiry = user.verification_expires_at

    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if not expiry or expiry < datetime.now(timezone.utc):
        return jsonify({
            "error": "Verification code has expired."
        }), 400

    user.is_verified = True

    user.verification_code_hash = None
    user.verification_expires_at = None

    db.session.commit()

    return jsonify({
        "message": "Email verified successfully. You can now log in."
    }), 200


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "error": "Email is required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    if user.is_verified:
        return jsonify({
            "message": "Email is already verified."
        }), 200

    code = f"{secrets.randbelow(1000000):06d}"

    user.verification_code_hash = generate_password_hash(code)
    user.verification_expires_at = (
        datetime.now(timezone.utc) + timedelta(minutes=10)
    )

    try:
        db.session.commit()

        send_verification_email(email, code)

        return jsonify({
            "message": "A new verification code has been sent to your email."
        }), 200

    except Exception:
        db.session.rollback()

        current_app.logger.exception("Resending verification code failed")

        return jsonify({
            "error": "Could not send verification code. Please try again."
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(
        user.password_hash, password
    ):
        return jsonify({
            "error": "Invalid email or password."
        }), 401

    if not user.is_verified:
        return jsonify({
            "error": "Please verify your email before logging in."
        }), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()

    new_access_token = create_access_token(
        identity=user_id
    )

    return jsonify({
        "access_token": new_access_token
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({
            "error": "User not found."
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }), 200
