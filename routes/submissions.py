from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Report, District
from schemas import ReportSchema

submissions_bp = Blueprint("submissions", __name__)

report_schema = ReportSchema()

SEVERITY_LEVELS = ["Critical", "High", "Moderate", "Low"]


@submissions_bp.route("", methods=["POST"])
@jwt_required()
def create_submission():
    data = request.get_json() or {}

    required = [
        "district_id",
        "location",
        "severity",
        "time_without_water",
        "description"
    ]

    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return jsonify({
            "error": f"Missing fields: {', '.join(missing)}"
        }), 400

    if data["severity"] not in SEVERITY_LEVELS:
        return jsonify({
            "error": f"Severity must be one of {SEVERITY_LEVELS}"
        }), 400

    try:
        district_id = int(data["district_id"])
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid district or user ID"}), 400

    district = db.session.get(District, district_id)
    if not district:
        return jsonify({"error": "District not found"}), 404

    report = Report(
        user_id=user_id,
        district_id=district_id,
        location=data["location"].strip(),
        severity=data["severity"],
        time_without_water=str(data["time_without_water"]).strip(),
        description=data["description"].strip()
    )

    db.session.add(report)
    db.session.commit()

    return jsonify({
        "message": "Report submitted successfully",
        "report": report_schema.dump(report)
    }), 201