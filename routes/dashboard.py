from datetime import date, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from models import Report, District


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


def success_response(message, data):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), 200


def error_response(message):
    return jsonify({
        "success": False,
        "message": message
    }), 500


def get_status_count(status):
    return Report.query.filter(
        func.lower(Report.status) == status.lower()
    ).count()


# 1. Dashboard summary
@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    try:
        data = {
            "total_reports": Report.query.count(),
            "pending_reports": get_status_count("pending"),
            "verified_reports": get_status_count("verified"),
            "resolved_reports": get_status_count("resolved"),
            "affected_districts": (
                District.query
                .join(Report, Report.district_id == District.id)
                .distinct()
                .count()
            )
        }

        return success_response(
            "Dashboard summary retrieved successfully.",
            data
        )
    except Exception:
        return error_response("Unable to retrieve dashboard summary.")


# 2. Recent reports
@dashboard_bp.route("/recent-reports", methods=["GET"])
@jwt_required()
def get_recent_reports():
    try:
        reports = (
            Report.query
            .order_by(Report.created_at.desc())
            .limit(10)
            .all()
        )

        data = [{
            "id": report.id,
            "status": report.status,
            "district": report.district.name if report.district else None,
            "location": report.location,
            "severity": report.severity,
            "created_at": (
                report.created_at.isoformat()
                if report.created_at else None
            )
        } for report in reports]

        return success_response(
            "Recent reports retrieved successfully.",
            data
        )
    except Exception:
        return error_response("Unable to retrieve recent reports.")


# 3. Affected areas
@dashboard_bp.route("/affected-areas", methods=["GET"])
@jwt_required()
def get_affected_areas():
    try:
        results = (
            Report.query
            .join(District, Report.district_id == District.id)
            .with_entities(
                District.id.label("district_id"),
                District.name.label("district_name"),
                func.count(Report.id).label("total_reports")
            )
            .group_by(District.id, District.name)
            .order_by(func.count(Report.id).desc())
            .all()
        )

        data = [{
            "district_id": area.district_id,
            "district": area.district_name,
            "total_reports": area.total_reports
        } for area in results]

        return success_response(
            "Affected areas retrieved successfully.",
            data
        )
    except Exception:
        return error_response("Unable to retrieve affected areas.")


# 4. Seven-day report trends
@dashboard_bp.route("/trends", methods=["GET"])
@jwt_required()
def get_report_trends():
    try:
        today = date.today()
        start_date = today - timedelta(days=6)

        reports = Report.query.filter(
            Report.created_at >= start_date
        ).all()

        daily_counts = {
            (start_date + timedelta(days=i)).isoformat(): 0
            for i in range(7)
        }

        for report in reports:
            if report.created_at:
                report_date = report.created_at.date().isoformat()

                if report_date in daily_counts:
                    daily_counts[report_date] += 1

        data = [
            {"date": day, "total_reports": count}
            for day, count in daily_counts.items()
        ]

        return success_response(
            "Report trends retrieved successfully.",
            data
        )
    except Exception:
        return error_response("Unable to retrieve report trends.")


# 5. Top five affected districts
@dashboard_bp.route("/top-affected-areas", methods=["GET"])
@jwt_required()
def get_top_affected_areas():
    try:
        results = (
            Report.query
            .join(District, Report.district_id == District.id)
            .with_entities(
                District.name.label("district_name"),
                func.count(Report.id).label("total_reports")
            )
            .group_by(District.id, District.name)
            .order_by(func.count(Report.id).desc())
            .limit(5)
            .all()
        )

        data = [{
            "district": area.district_name,
            "total_reports": area.total_reports
        } for area in results]

        return success_response(
            "Top affected areas retrieved successfully.",
            data
        )
    except Exception:
        return error_response("Unable to retrieve top affected areas.")