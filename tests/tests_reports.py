from extensions import db
from models.district import District


def test_only_approved_returned(client, make_submission):
    make_submission(status="approved")
    make_submission(status="pending")
    res = client.get("/api/reports")
    assert res.status_code == 200
    assert len(res.get_json()) == 1
    assert res.get_json()[0]["status"] == "approved"


def test_sorted_by_severity_then_days(client, make_submission):
    make_submission(severity="low", days=30)
    make_submission(severity="critical", days=3)
    make_submission(severity="critical", days=10)
    make_submission(severity="high", days=7)
    res = client.get("/api/reports").get_json()
    assert [(r["severity"], r["time_without_water"]) for r in res] == [
        ("critical", 10), ("critical", 3), ("high", 7), ("low", 30),
    ]


def test_district_filter(client, district, make_submission):
    other = District(name="Kasarani")
    db.session.add(other)
    db.session.commit()
    make_submission(district_id=district.id)
    make_submission(district_id=other.id)
    res = client.get(f"/api/reports?district_id={other.id}").get_json()
    assert len(res) == 1
    assert res[0]["district"] == "Kasarani"