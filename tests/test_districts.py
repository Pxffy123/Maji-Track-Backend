import pytest
from flask import Flask
from models import db
from routes.districts import districts_bp


@pytest.fixture
def client():
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(test_app)
    test_app.register_blueprint(districts_bp)

    with test_app.app_context():
        db.create_all()
        yield test_app.test_client()
        db.session.remove()
        db.drop_all()


def test_get_districts_empty(client):
    res = client.get("/api/districts")
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_district(client):
    res = client.post("/api/districts", json={"name": "Kibera"})
    assert res.status_code == 201
    assert res.get_json()["name"] == "Kibera"


def test_create_district_without_name(client):
    res = client.post("/api/districts", json={})
    assert res.status_code == 400


def test_get_one_district(client):
    created = client.post("/api/districts", json={"name": "Kibera"}).get_json()
    res = client.get(f"/api/districts/{created['id']}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Kibera"


def test_get_missing_district(client):
    res = client.get("/api/districts/999")
    assert res.status_code == 404


def test_update_district(client):
    created = client.post("/api/districts", json={"name": "Kibera"}).get_json()
    res = client.patch(f"/api/districts/{created['id']}", json={"name": "Mathare"})
    assert res.status_code == 200
    assert res.get_json()["name"] == "Mathare"


def test_delete_district(client):
    created = client.post("/api/districts", json={"name": "Kibera"}).get_json()
    res = client.delete(f"/api/districts/{created['id']}")
    assert res.status_code == 200
    assert client.get(f"/api/districts/{created['id']}").status_code == 404
