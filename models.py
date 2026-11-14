
from datetime import datetime, timezone

from extensions import db



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="resident", nullable=False)

    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_code_hash = db.Column(db.String(255), nullable=True)
    verification_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Reports submitted by this user
    reports = db.relationship(
        "Report",
        foreign_keys="Report.user_id",
        back_populates="resident"
    )

    # Reports reviewed by this admin
    reviewed_reports = db.relationship(
        "Report",
        foreign_keys="Report.reviewed_by",
        back_populates="reviewer"
    )

class District(db.Model):
    __tablename__ = "districts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    reports = db.relationship("Report", back_populates="district")


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey("districts.id"), nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    location = db.Column(db.String(150), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    time_without_water = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    resident = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="reports"
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewed_by],
        back_populates="reviewed_reports"
    )

    district = db.relationship("District", back_populates="reports")
