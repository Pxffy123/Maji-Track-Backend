def payload(district, **overrides):
    data = {
        "district_id": district.id,
        "location": "Umoja 1",
        "severity": "Critical",
        "time_without_water": "3 weeks",
        "description": "No running water in our neighbourhood.",
    }
    data.update(overrides)
    return data


def test_create_report_success(client, auth_headers, district):
    res = client.post("/api/submissions", json=payload(district), headers=auth_headers)
    assert res.status_code == 201
    body = res.get_json()
    assert body["status"] == "Pending"
    assert body["district"] == "Embakasi"
    assert body["reporter"] == "fiona"


def test_severity_is_case_insensitive(client, auth_headers, district):
    res = client.post("/api/submissions",
                      json=payload(district, severity="critical"), headers=auth_headers)
    assert res.status_code == 201
    assert res.get_json()["severity"] == "Critical"


def test_requires_login(client, district):
    res = client.post("/api/submissions", json=payload(district))
    assert res.status_code == 401


def test_missing_fields(client, auth_headers):
    res = client.post("/api/submissions", json={"location": "Umoja 1"}, headers=auth_headers)
    assert res.status_code == 400


def test_description_required(client, auth_headers, district):
    res = client.post("/api/submissions",
                      json=payload(district, description=""), headers=auth_headers)
    assert res.status_code == 400


def test_invalid_severity(client, auth_headers, district):
    res = client.post("/api/submissions",
                      json=payload(district, severity="Extreme"), headers=auth_headers)
    assert res.status_code == 400


def test_unknown_district(client, auth_headers, district):
    res = client.post("/api/submissions",
                      json=payload(district, district_id=999), headers=auth_headers)
    assert res.status_code == 404