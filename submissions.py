from datetime import datetime
from extensions import db

SEVERITY_LEVELS = ["low", "medium", "high", "critical"]
STATUSES = ["pending", "approved"]


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey("districts.id"), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    time_without_water = db.Column(db.Integer, nullable=False)  # in days
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="submissions")
    district = db.relationship("District", backref="submissions")

    def to_dict(self):
        return {
            "id": self.id,
            "location": self.location,
            "district": self.district.name,
            "severity": self.severity,
            "time_without_water": self.time_without_water,
            "description": self.description,
            "status": self.status,
            "reporter": self.user.name,
            "created_at": self.created_at.isoformat(),
        }