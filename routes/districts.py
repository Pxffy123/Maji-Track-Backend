from flask import Blueprint, request, jsonify
from models import db, District

districts_bp = Blueprint("districts", __name__, url_prefix="/api/districts")


@districts_bp.route("", methods=["GET"])
def get_districts():
    districts = District.query.all()
    return jsonify([{"id": d.id, "name": d.name} for d in districts]), 200


@districts_bp.route("/<int:district_id>", methods=["GET"])
def get_district(district_id):
    d = db.session.get(District, district_id)
    if not d:
        return jsonify({"error": "District not found"}), 404
    return jsonify({"id": d.id, "name": d.name}), 200


@districts_bp.route("", methods=["POST"])
def create_district():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    d = District(name=name)
    db.session.add(d)
    db.session.commit()
    return jsonify({"id": d.id, "name": d.name}), 201


@districts_bp.route("/<int:district_id>", methods=["PATCH"])
def update_district(district_id):
    d = db.session.get(District, district_id)
    if not d:
        return jsonify({"error": "District not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        d.name = data["name"].strip()
    db.session.commit()
    return jsonify({"id": d.id, "name": d.name}), 200


@districts_bp.route("/<int:district_id>", methods=["DELETE"])
def delete_district(district_id):
    d = db.session.get(District, district_id)
    if not d:
        return jsonify({"error": "District not found"}), 404

    db.session.delete(d)
    db.session.commit()
    return jsonify({"message": "District deleted"}), 200
