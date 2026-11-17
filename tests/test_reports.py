from extensions import db
from models import District


def test_only_approved_returned(client, make_report):
    make_report(status="Approved")
    make_report(status="Pending")
    res = client.get("/api/reports")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["status"] == "Approved"


def test_sorted_by_severity(client, make_report):
    for sev in ["Low", "Critical", "Moderate", "High"]:
        make_report(severity=sev)
    res = client.get("/api/reports").get_json()
    assert [r["severity"] for r in res] == ["Critical", "High", "Moderate", "Low"]


def test_district_filter(client, district, make_report):
    other = District(name="Kasarani")
    db.session.add(other)
    db.session.commit()
    make_report(district_id=district.id)
    make_report(district_id=other.id)
    res = client.get(f"/api/reports?district_id={other.id}").get_json()
    assert len(res) == 1
    assert res[0]["district"] == "Kasarani"


def test_response_fields(client, make_report):
    make_report()
    report = client.get("/api/reports").get_json()[0]
    for field in ["id", "location", "district", "severity",
                  "time_without_water", "description", "status", "created_at"]:
        assert field in report