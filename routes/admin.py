
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Report
from schemas import ReportSchema

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)


# Get all pending reports
@admin_bp.route("/reports/pending", methods=["GET"])
@jwt_required()
def get_pending_reports():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    reports = Report.query.filter_by(status="Pending").all()

    return jsonify(reports_schema.dump(reports)), 200


# Get all approved reports
@admin_bp.route("/reports/approved", methods=["GET"])
@jwt_required()
def get_approved_reports():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    reports = Report.query.filter_by(status="Approved").all()

    return jsonify(reports_schema.dump(reports)), 200


# Approve a report
@admin_bp.route("/reports/<int:report_id>/approve", methods=["PATCH"])
@jwt_required()
def approve_report(report_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    report = db.session.get(Report, report_id)

    if not report:
        return jsonify({"error": "Report not found"}), 404

    if report.status != "Pending":
        return jsonify({"error": "Report is not pending"}), 400

    report.status = "Approved"
    report.reviewed_by = current_user_id

    db.session.commit()

    return jsonify({
        "message": "Report approved successfully",
        "report": report_schema.dump(report)
    }), 200


# Reject a report
@admin_bp.route("/reports/<int:report_id>/reject", methods=["PATCH"])
@jwt_required()
def reject_report(report_id):
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user or user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403

    report = db.session.get(Report, report_id)

    if not report:
        return jsonify({"error": "Report not found"}), 404

    if report.status != "Pending":
        return jsonify({"error": "Report is not pending"}), 400

    report.status = "Rejected"
    report.reviewed_by = current_user_id

    db.session.commit()

    return jsonify({
        "message": "Report rejected successfully",
        "report": report_schema.dump(report)
    }), 200
