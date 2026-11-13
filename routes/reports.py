from flask import Blueprint, request, jsonify
from models.submission import Submission

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@reports_bp.route("", methods=["GET"])
def get_reports():
    query = Submission.query.filter_by(status="approved")

    district_id = request.args.get("district_id", type=int)
    if district_id:
        query = query.filter_by(district_id=district_id)

    reports = sorted(
        query.all(),
        key=lambda s: (SEVERITY_ORDER[s.severity], -s.time_without_water),
    )
    return jsonify([r.to_dict() for r in reports]), 200