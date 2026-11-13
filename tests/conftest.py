import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from extensions import db, init_extensions
from models import User, District, Report
from routes.submissions import submissions_bp
from routes.reports import reports_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        JWT_SECRET_KEY="test-secret",
    )
    init_extensions(app)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def district(app):
    d = District(name="Embakasi")
    db.session.add(d)
    db.session.commit()
    return d


@pytest.fixture
def user(app):
    u = User(username="fiona", email="fiona@example.com",
             password_hash="x", role="resident")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def auth_headers(user):
    token = create_access_token(identity=str(user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_report(user, district):
    def _make(severity="High", status="Approved", district_id=None):
        r = Report(
            user_id=user.id,
            district_id=district_id or district.id,
            location="Umoja 1",
            severity=severity,
            time_without_water="3 weeks",
            description="No running water",
            status=status,
        )
        db.session.add(r)
        db.session.commit()
        return r
    return _make