import pytest
from flask import Flask
from extensions import db
from models import District
from routes.districts import districts_bp


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(districts_bp, url_prefix="/api/districts")

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def add_district(name):
    d = District(name=name)
    db.session.add(d)
    db.session.commit()
    return d


def test_get_districts_empty(client):
    res = client.get("/api/districts")
    assert res.status_code == 200
    assert res.get_json() == []


def test_get_districts_sorted_by_name(client):
    add_district("Mathare")
    add_district("Kibera")
    res = client.get("/api/districts")
    names = [d["name"] for d in res.get_json()]
    assert names == ["Kibera", "Mathare"]


def test_get_one_district(client):
    d = add_district("Kibera")
    res = client.get(f"/api/districts/{d.id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Kibera"


def test_get_missing_district(client):
    res = client.get("/api/districts/999")
    assert res.status_code == 404


def test_reports_of_missing_district(client):
    res = client.get("/api/districts/999/reports")
    assert res.status_code == 404