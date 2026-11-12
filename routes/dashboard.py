from datetime import date, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from models import Report, District, County


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def success_response(message, data):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), 200


def error_response(message, status_code=500):
    return jsonify({
        "success": False,
        "message": message
    }), status_code


def get_status_count(status):
    return Report.query.filter(
        func.lower(Report.status) == status.lower()
    ).count()


# --------------------------------------------------
# 1. DASHBOARD SUMMARY
# --------------------------------------------------

@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_dashboard_summary():
    try:
        total_reports = Report.query.count()

        pending_reports = get_status_count("pending")
        verified_reports = get_status_count("verified")
        resolved_reports = get_status_count("resolved")

        affected_districts = (
            db_districts_with_reports()
        )

        affected_counties = (
            db_counties_with_reports()
        )

        data = {
            "total_reports": total_reports,
            "pending_reports": pending_reports,
            "verified_reports": verified_reports,
            "resolved_reports": resolved_reports,
            "affected_districts": affected_districts,
            "affected_counties": affected_counties
        }

        return success_response(
            "Dashboard summary retrieved successfully.",
            data
        )

    except Exception:
        return error_response(
            "Unable to retrieve dashboard summary."
        )


# --------------------------------------------------
# 2. RECENT WATER SHORTAGE REPORTS
# --------------------------------------------------

@dashboard_bp.route("/recent-reports", methods=["GET"])
@jwt_required()
def get_recent_reports():
    try:
        reports = (
            Report.query
            .outerjoin(
                District,
                Report.district_id == District.id
            )
            .outerjoin(
                County,
                District.county_id == County.id
            )
            .order_by(Report.created_at.desc())
            .limit(10)
            .all()
        )

        data = []

        for report in reports:
            data.append({
                "id": report.id,
                "status": report.status,
                "district": (
                    report.district.name
                    if report.district else None
                ),
                "county": (
                    report.district.county.name
                    if report.district
                    and report.district.county else None
                ),
                "created_at": (
                    report.created_at.isoformat()
                    if report.created_at else None
                )
            })

        return success_response(
            "Recent reports retrieved successfully.",
            data
        )

    except Exception:
        return error_response(
            "Unable to retrieve recent reports."
        )


# --------------------------------------------------
# 3. AFFECTED AREAS
# --------------------------------------------------

@dashboard_bp.route("/affected-areas", methods=["GET"])
@jwt_required()
def get_affected_areas():
    try:
        results = (
            Report.query
            .join(
                District,
                Report.district_id == District.id
            )
            .outerjoin(
                County,
                District.county_id == County.id
            )
            .with_entities(
                District.id.label("district_id"),
                District.name.label("district_name"),
                County.name.label("county_name"),
                func.count(Report.id).label("report_count")
            )
            .group_by(
                District.id,
                District.name,
                County.name
            )
            .order_by(
                func.count(Report.id).desc()
            )
            .all()
        )

        data = []

        for area in results:
            data.append({
                "district_id": area.district_id,
                "district": area.district_name,
                "county": area.county_name,
                "total_reports": area.report_count
            })

        return success_response(
            "Affected areas retrieved successfully.",
            data
        )

    except Exception:
        return error_response(
            "Unable to retrieve affected areas."
        )


# --------------------------------------------------
# 4. WATER SHORTAGE REPORT TRENDS
# --------------------------------------------------

@dashboard_bp.route("/trends", methods=["GET"])
@jwt_required()
def get_report_trends():
    try:
        today = date.today()
        start_date = today - timedelta(days=6)

        reports = Report.query.filter(
            Report.created_at >= start_date
        ).all()

        daily_counts = {}

        for i in range(7):
            current_day = start_date + timedelta(days=i)
            daily_counts[current_day.isoformat()] = 0

        for report in reports:
            if report.created_at:
                report_date = report.created_at.date().isoformat()

                if report_date in daily_counts:
                    daily_counts[report_date] += 1

        data = [
            {
                "date": report_date,
                "total_reports": count
            }
            for report_date, count in daily_counts.items()
        ]

        return success_response(
            "Report trends retrieved successfully.",
            data
        )

    except Exception:
        return error_response(
            "Unable to retrieve report trends."
        )


# --------------------------------------------------
# 5. MOST REPORTED AREAS
# --------------------------------------------------

@dashboard_bp.route("/top-affected-areas", methods=["GET"])
@jwt_required()
def get_top_affected_areas():
    try:
        results = (
            Report.query
            .join(
                District,
                Report.district_id == District.id
            )
            .outerjoin(
                County,
                District.county_id == County.id
            )
            .with_entities(
                District.name.label("district_name"),
                County.name.label("county_name"),
                func.count(Report.id).label("total_reports")
            )
            .group_by(
                District.id,
                District.name,
                County.name
            )
            .order_by(
                func.count(Report.id).desc()
            )
            .limit(5)
            .all()
        )

        data = []

        for area in results:
            data.append({
                "district": area.district_name,
                "county": area.county_name,
                "total_reports": area.total_reports
            })

        return success_response(
            "Top affected areas retrieved successfully.",
            data
        )

    except Exception:
        return error_response(
            "Unable to retrieve top affected areas."
        )


# --------------------------------------------------
# HELPER QUERIES
# --------------------------------------------------

def db_districts_with_reports():
    return (
        db_query_districts()
    )


def db_query_districts():
    return (
        District.query
        .join(Report, Report.district_id == District.id)
        .distinct()
        .count()
    )


def db_counties_with_reports():
    return (
        County.query
        .join(District, District.county_id == County.id)
        .join(Report, Report.district_id == District.id)
        .distinct()
        .count()
    )