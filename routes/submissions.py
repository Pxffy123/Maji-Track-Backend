from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Report, District
from routes.reports import report_to_dict

submissions_bp = Blueprint("submissions", __name__, url_prefix="/api/submissions")
SEVERITY_LEVELS = ["Critical", "High", "Moderate", "Low"]


@submissions_bp.route("", methods=["POST"])
@jwt_required()
def create_submission():
    data = request.get_json() or {}

    required = ["district_id", "location", "severity", "time_without_water", "description"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    severity = next(
        (s for s in SEVERITY_LEVELS if s.lower() == str(data["severity"]).strip().lower()),
        None,
    )
    if severity is None:
        return jsonify({"error": f"Severity must be one of {SEVERITY_LEVELS}"}), 400

    if not db.session.get(District, data["district_id"]):
        return jsonify({"error": "District not found"}), 404

    report = Report(
        user_id=int(get_jwt_identity()),
        district_id=data["district_id"],
        location=str(data["location"]).strip(),
        severity=severity,
        time_without_water=str(data["time_without_water"]).strip(),
        description=str(data["description"]).strip(),
    )
    db.session.add(report)
    db.session.commit()

    return jsonify(report_to_dict(report)), 201