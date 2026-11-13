from flask import Blueprint, request, jsonify
from models import Report

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def report_to_dict(r):
    return {
        "id": r.id,
        "location": r.location,
        "district": r.district.name,
        "severity": r.severity,
        "time_without_water": r.time_without_water,
        "description": r.description,
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