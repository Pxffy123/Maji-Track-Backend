def payload(district, **overrides):
    data = {
        "district_id": district.id,
        "location": "Umoja 1",
        "severity": "critical",
        "time_without_water": 21,
        "description": "No water for weeks",
    }
    data.update(overrides)
    return data


def test_create_submission_success(client, auth_headers, district):
    res = client.post("/api/submissions", json=payload(district), headers=auth_headers)
    assert res.status_code == 201
    body = res.get_json()
    assert body["status"] == "pending"
    assert body["district"] == "Embakasi"


def test_requires_login(client, district):
    res = client.post("/api/submissions", json=payload(district))
    assert res.status_code == 401


def test_missing_fields(client, auth_headers):
    res = client.post("/api/submissions", json={"location": "Umoja 1"}, headers=auth_headers)
    assert res.status_code == 400


def test_invalid_severity(client, auth_headers, district):
    res = client.post("/api/submissions",
                      json=payload(district, severity="extreme"), headers=auth_headers)
    assert res.status_code == 400


def test_invalid_days(client, auth_headers, district):
    for bad in ["three weeks", 0, -4]:
        res = client.post("/api/submissions",
                          json=payload(district, time_without_water=bad), headers=auth_headers)
        assert res.status_code == 400


def test_unknown_district(client, auth_headers, district):
    res = client.post("/api/submissions",
                      json=payload(district, district_id=999), headers=auth_headers)
    assert res.status_code == 404