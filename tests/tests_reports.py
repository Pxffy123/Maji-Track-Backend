from flask import Blueprint, request, jsonify

from models import Report
from schemas import ReportSchema

reports_bp = Blueprint("reports", __name__)

reports_schema = ReportSchema(many=True)

SEVERITY_ORDER = {
    "Critical": 0,
    "High": 1,
    "Moderate": 2,
    "Low": 3
}


@reports_bp.route("", methods=["GET"])
def get_reports():
    query = Report.query.filter_by(status="Approved")

    district_id = request.args.get("district_id", type=int)

    if district_id is not None:
        query = query.filter_by(district_id=district_id)

    reports = query.all()

    reports.sort(
        key=lambda report: (
            SEVERITY_ORDER.get(report.severity, 4),
            -report.created_at.timestamp()
        )
    )

    return jsonify(reports_schema.dump(reports)), 200