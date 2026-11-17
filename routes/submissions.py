from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Report, District, User
from routes.reports import report_to_dict
import cloudinary.uploader
from werkzeug.utils import secure_filename
submissions_bp = Blueprint("submissions", __name__, url_prefix="/api/submissions")

SEVERITY_LEVELS = ["Critical", "High", "Moderate", "Low"]


@submissions_bp.route("", methods=["POST"])
@jwt_required()
def create_submission():
    # Accept both normal JSON and multipart form data
    data = request.form if request.form else (request.get_json(silent=True) or {})

    required = [
        "district_id",
        "location",
        "severity",
        "time_without_water",
        "description"
    ]

    missing = [f for f in required if data.get(f) in (None, "")]

    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    severity = next(
        (s for s in SEVERITY_LEVELS if s.lower() == str(data["severity"]).strip().lower()),
        None,
    )

    if severity is None:
        return jsonify({"error": f"Severity must be one of {SEVERITY_LEVELS}"}), 400

    try:
        district_id = int(data["district_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid district_id"}), 400

    if not db.session.get(District, district_id):
        return jsonify({"error": "District not found"}), 404

    # Upload image if the resident attached one
    image_url = None
    uploaded_image = request.files.get("image")

    if uploaded_image and uploaded_image.filename:
        filename = secure_filename(uploaded_image.filename)
        allowed_extensions = {"png", "jpg", "jpeg", "webp"}

        if "." not in filename or filename.rsplit(".", 1)[1].lower() not in allowed_extensions:
            return jsonify({"error": "Only PNG, JPG, JPEG and WEBP images are allowed"}), 400

        try:
            from PIL import Image

            # Check that the uploaded file is a valid image
            img = Image.open(uploaded_image.stream)
            img.verify()
            uploaded_image.stream.seek(0)

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                uploaded_image,
                folder="maji_track/reports",
                resource_type="image"
            )

            image_url = result["secure_url"]

        except Exception:
            return jsonify({"error": "Image upload failed. Please try another image."}), 400

    report = Report(
        user_id=int(get_jwt_identity()),
        district_id=district_id,
        location=str(data["location"]).strip(),
        severity=severity,
        time_without_water=str(data["time_without_water"]).strip(),
        description=str(data["description"]).strip(),
        image_url=image_url
    )

    db.session.add(report)
    db.session.commit()

    return jsonify(report_to_dict(report)), 201

def get_editable_report(report_id):
    """Return (report, None) if the current user may change it, else (None, error_response)."""
    report = db.session.get(Report, report_id)
    if not report:
        return None, (jsonify({"error": "Report not found"}), 404)

    user = db.session.get(User, int(get_jwt_identity()))
    if user.role != "admin":
        if report.user_id != user.id:
            return None, (jsonify({"error": "Not allowed"}), 403)
        if report.status.lower() != "pending":
            return None, (jsonify({"error": "Only pending reports can be changed"}), 403)
    return report, None


@submissions_bp.route("/<int:report_id>", methods=["PATCH"])
@jwt_required()
def update_submission(report_id):
    report, error = get_editable_report(report_id)
    if error:
        return error

    data = request.get_json() or {}

    if "severity" in data:
        severity = next(
            (s for s in SEVERITY_LEVELS if s.lower() == str(data["severity"]).strip().lower()),
            None,
        )
        if severity is None:
            return jsonify({"error": f"Severity must be one of {SEVERITY_LEVELS}"}), 400
        report.severity = severity

    if "district_id" in data:
        if not db.session.get(District, data["district_id"]):
            return jsonify({"error": "District not found"}), 404
        report.district_id = data["district_id"]

    for field in ["location", "time_without_water", "description"]:
        if field in data:
            value = str(data[field]).strip()
            if not value:
                return jsonify({"error": f"{field} cannot be empty"}), 400
            setattr(report, field, value)

    db.session.commit()
    return jsonify(report_to_dict(report)), 200


@submissions_bp.route("/<int:report_id>", methods=["DELETE"])
@jwt_required()
def delete_submission(report_id):
    report, error = get_editable_report(report_id)
    if error:
        return error

    db.session.delete(report)
    db.session.commit()
    return jsonify({"message": "Report deleted"}), 200
