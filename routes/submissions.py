from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.submission import Submission, SEVERITY_LEVELS
from models.district import District

submissions_bp = Blueprint("submissions", __name__, url_prefix="/api/submissions")


@submissions_bp.route("", methods=["POST"])
@jwt_required()
def create_submission():
    data = request.get_json() or {}

    required = ["district_id", "location", "severity", "time_without_water"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if data["severity"] not in SEVERITY_LEVELS:
        return jsonify({"error": f"Severity must be one of {SEVERITY_LEVELS}"}), 400

    try:
        days = int(data["time_without_water"])
    except (TypeError, ValueError):
        return jsonify({"error": "time_without_water must be a number of days"}), 400
    if days <= 0:
        return jsonify({"error": "time_without_water must be greater than 0"}), 400

    if not db.session.get(District, data["district_id"]):
        return jsonify({"error": "District not found"}), 404

    submission = Submission(
        user_id=int(get_jwt_identity()),
        district_id=data["district_id"],
        location=data["location"].strip(),
        severity=data["severity"],
        time_without_water=days,
        description=data.get("description"),
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify(submission.to_dict()), 201