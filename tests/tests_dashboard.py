import pytest

from datetime import datetime, timezone

from flask import Flask
from flask_jwt_extended import create_access_token

from extensions import db, jwt
from models import User, District, Report
from routes.dashboard import dashboard_bp


@pytest.fixture
def app():
    app = Flask(__name__)

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-jwt-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_data(app):
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="test-password",
            role="resident"
        )

        district = District(name="South C")

        db.session.add_all([user, district])
        db.session.commit()

        report = Report(
            user_id=user.id,
            district_id=district.id,
            location="South C",
            severity="High",
            time_without_water="3 days",
            description="No water supply",
            status="Pending",
            created_at=datetime.now(timezone.utc)
        )

        db.session.add(report)
        db.session.commit()

        return {
            "user_id": user.id,
            "district_id": district.id,
            "report_id": report.id
        }


@pytest.fixture
def auth_headers(app, test_data):
    with app.app_context():
        token = create_access_token(
            identity=str(test_data["user_id"])
        )

        return {
            "Authorization": f"Bearer {token}"
        }


def test_dashboard_requires_authentication(client):
    response = client.get("/api/dashboard/summary")

    assert response.status_code == 401

def test_dashboard_summary(client, test_data, auth_headers):
    response = client.get(
        "/api/dashboard/summary",
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["success"] is True
    assert result["data"]["total_reports"] == 1
    assert result["data"]["pending_reports"] == 1
    assert result["data"]["verified_reports"] == 0
    assert result["data"]["resolved_reports"] == 0
    assert result["data"]["affected_districts"] == 1

def test_recent_reports(client, test_data, auth_headers):
    response = client.get(
        "/api/dashboard/recent-reports",
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["success"] is True
    assert len(result["data"]) == 1

    report = result["data"][0]

    assert report["id"] == test_data["report_id"]
    assert report["status"] == "Pending"
    assert report["district"] == "South C"
    assert report["location"] == "South C"
    assert report["severity"] == "High"

def test_affected_areas(client, test_data, auth_headers):
    response = client.get(
        "/api/dashboard/affected-areas",
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["success"] is True
    assert len(result["data"]) == 1

    area = result["data"][0]

    assert area["district_id"] == test_data["district_id"]
    assert area["district"] == "South C"
    assert area["total_reports"] == 1

def test_report_trends(client, test_data, auth_headers):
    response = client.get(
        "/api/dashboard/trends",
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["success"] is True
    assert len(result["data"]) == 7
    assert sum(day["total_reports"] for day in result["data"]) == 1
    assert all(
        "date" in day and "total_reports" in day
        for day in result["data"]
    )

def test_top_affected_areas(client, test_data, auth_headers):
    response = client.get(
        "/api/dashboard/top-affected-areas",
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.get_json()

    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["district"] == "South C"
    assert result["data"][0]["total_reports"] == 1