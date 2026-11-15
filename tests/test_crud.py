from extensions import db
from models import Report


# ---------- READ ONE ----------

def test_get_approved_report_is_public(client, make_report):
    r = make_report(status="Approved")
    res = client.get(f"/api/reports/{r.id}")
    assert res.status_code == 200
    assert res.get_json()["id"] == r.id


def test_get_pending_hidden_from_anonymous(client, make_report):
    r = make_report(status="Pending")
    assert client.get(f"/api/reports/{r.id}").status_code == 404


def test_get_pending_visible_to_owner(client, make_report, auth_headers):
    r = make_report(status="Pending")
    assert client.get(f"/api/reports/{r.id}", headers=auth_headers).status_code == 200


def test_get_pending_hidden_from_other_user(client, make_report, other_headers):
    r = make_report(status="Pending")
    assert client.get(f"/api/reports/{r.id}", headers=other_headers).status_code == 404


def test_get_pending_visible_to_admin(client, make_report, admin_headers):
    r = make_report(status="Pending")
    assert client.get(f"/api/reports/{r.id}", headers=admin_headers).status_code == 200


def test_get_missing_report(client):
    assert client.get("/api/reports/999").status_code == 404


# ---------- UPDATE ----------

def test_owner_can_update_pending(client, make_report, auth_headers):
    r = make_report(status="Pending")
    res = client.patch(f"/api/submissions/{r.id}",
                       json={"location": "Kayole", "severity": "low"},
                       headers=auth_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["location"] == "Kayole"
    assert body["severity"] == "Low"


def test_update_requires_login(client, make_report):
    r = make_report(status="Pending")
    assert client.patch(f"/api/submissions/{r.id}", json={"location": "X"}).status_code == 401


def test_other_user_cannot_update(client, make_report, other_headers):
    r = make_report(status="Pending")
    res = client.patch(f"/api/submissions/{r.id}",
                       json={"location": "X"}, headers=other_headers)
    assert res.status_code == 403


def test_owner_cannot_update_approved(client, make_report, auth_headers):
    r = make_report(status="Approved")
    res = client.patch(f"/api/submissions/{r.id}",
                       json={"location": "X"}, headers=auth_headers)
    assert res.status_code == 403


def test_admin_can_update_approved(client, make_report, admin_headers):
    r = make_report(status="Approved")
    res = client.patch(f"/api/submissions/{r.id}",
                       json={"location": "Admin Edit"}, headers=admin_headers)
    assert res.status_code == 200


def test_update_invalid_severity(client, make_report, auth_headers):
    r = make_report(status="Pending")
    res = client.patch(f"/api/submissions/{r.id}",
                       json={"severity": "Extreme"}, headers=auth_headers)
    assert res.status_code == 400


def test_update_cannot_change_status(client, make_report, auth_headers):
    r = make_report(status="Pending")
    client.patch(f"/api/submissions/{r.id}",
                 json={"status": "Approved"}, headers=auth_headers)
    assert db.session.get(Report, r.id).status == "Pending"


def test_update_missing_report(client, auth_headers):
    res = client.patch("/api/submissions/999", json={"location": "X"}, headers=auth_headers)
    assert res.status_code == 404


# ---------- DELETE ----------

def test_owner_can_delete_pending(client, make_report, auth_headers):
    r = make_report(status="Pending")
    res = client.delete(f"/api/submissions/{r.id}", headers=auth_headers)
    assert res.status_code == 200
    assert db.session.get(Report, r.id) is None


def test_delete_requires_login(client, make_report):
    r = make_report(status="Pending")
    assert client.delete(f"/api/submissions/{r.id}").status_code == 401


def test_other_user_cannot_delete(client, make_report, other_headers):
    r = make_report(status="Pending")
    assert client.delete(f"/api/submissions/{r.id}", headers=other_headers).status_code == 403


def test_owner_cannot_delete_approved(client, make_report, auth_headers):
    r = make_report(status="Approved")
    assert client.delete(f"/api/submissions/{r.id}", headers=auth_headers).status_code == 403


def test_admin_can_delete_approved(client, make_report, admin_headers):
    r = make_report(status="Approved")
    assert client.delete(f"/api/submissions/{r.id}", headers=admin_headers).status_code == 200