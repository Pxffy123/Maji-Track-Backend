import pytest
from flask import Flask
from config import TestingConfig
from extensions import db, init_extensions
from routes.auth import auth_bp
from models import User

@pytest.fixture
def client(monkeypatch):
    app = Flask(__name__)

    app.config.from_object(TestingConfig)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SECRET_KEY"] = "test-secret"
    app.config["JWT_SECRET_KEY"] = "test-jwt-secret"
    app.config["TESTING"] = True

    init_extensions(app)
    app.register_blueprint(auth_bp)

    monkeypatch.setattr(
        "routes.auth.send_verification_email",
        lambda email, code: None
    )

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
def test_register_requires_user_information(client):
    response = client.post("/auth/register", json={})
    assert response.status_code == 400

def test_verify_email_requires_code(client):
    response = client.post("/auth/verify-email", json={})
    assert response.status_code == 400

def test_login_requires_credentials(client):
    response = client.post("/auth/login", json={})
    assert response.status_code == 400

def test_login_with_wrong_credentials(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
def test_user_cannot_access_profile_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
def test_refresh_requires_refresh_token(client):
    response = client.post("/auth/refresh")
    assert response.status_code == 401