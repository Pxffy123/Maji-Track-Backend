
from flask import Blueprint, jsonify

from models import District, Report
from schemas import DistrictSchema, ReportSchema

districts_bp = Blueprint("districts", __name__)

district_schema = DistrictSchema()
districts_schema = DistrictSchema(many=True)
reports_schema = ReportSchema(many=True)


# Get all districts
@districts_bp.route("", methods=["GET"])
def get_districts():
    districts = District.query.order_by(District.name).all()
    return jsonify(districts_schema.dump(districts)), 200


# Get one district
@districts_bp.route("/<int:district_id>", methods=["GET"])
def get_district(district_id):
    district = District.query.get(district_id)

    if not district:
        return jsonify({"error": "District not found"}), 404

    return jsonify(district_schema.dump(district)), 200


# Get approved reports belonging to a district
@districts_bp.route("/<int:district_id>/reports", methods=["GET"])
def get_district_reports(district_id):
    district = District.query.get(district_id)

    if not district:
        return jsonify({"error": "District not found"}), 404

    reports = (
        Report.query
        .filter_by(district_id=district_id, status="Approved")
        .order_by(Report.created_at.desc())
        .all()
    )

    return jsonify(reports_schema.dump(reports)), 200
