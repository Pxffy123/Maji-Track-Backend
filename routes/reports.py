from flask import Blueprint, request, jsonify
from models import Report
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from extensions import db
from models import User

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

SEVERITY_ORDER = {"critical": 0, "high": 1, "moderate": 2, "low": 3}


def report_to_dict(r):
    return {
        "id": r.id,
        "location": r.location,
        "district": r.district.name,
        "district_id": r.district_id,
        "severity": r.severity,
        "time_without_water": r.time_without_water,
        "description": r.description,
        "image_url": r.image_url,
        "status": r.status,
        "reporter": r.resident.username,
        "created_at": r.created_at.isoformat(),
    }


@reports_bp.route("", methods=["GET"])
def get_reports():
    query = Report.query.filter(Report.status.ilike("approved"))

    district_id = request.args.get("district_id", type=int)
    if district_id:
        query = query.filter_by(district_id=district_id)

    reports = sorted(
        query.all(),
        key=lambda r: SEVERITY_ORDER.get(r.severity.lower(), 99),
    )
    return jsonify([report_to_dict(r) for r in reports]), 200

@reports_bp.route("/<int:report_id>", methods=["GET"])
def get_report(report_id):
    report = db.session.get(Report, report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404

    if report.status.lower() != "approved":
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity is None:
            return jsonify({"error": "Report not found"}), 404
        user = db.session.get(User, int(identity))
        if user.role != "admin" and report.user_id != user.id:
            return jsonify({"error": "Report not found"}), 404

    return jsonify(report_to_dict(report)), 200
