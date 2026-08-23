from web.app import app


def test_planets_api():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 9

    assert len(data["planets"]) == 9


def test_planets_api_contains_jupiter():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets"
    )

    data = response.get_json()

    names = [
        planet["name"]
        for planet in data["planets"]
    ]

    assert "Jupiter" in names

def test_planet_api_returns_jupiter():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/jupiter"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "Jupiter"

    assert (
        data["skyfield_object"]
        == "jupiter barycenter"
    )


def test_planet_api_invalid_planet():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/not-a-planet"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == (
        "Invalid planetary body."
    )

def test_overview_api():

    client = app.test_client()

    response = client.get(
        "/api/v1/overview"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "calculation_time" in data
    assert "count" in data
    assert "objects" in data

    assert data["count"] == 9
    assert len(data["objects"]) == 9


def test_overview_api_contains_earth():

    client = app.test_client()

    response = client.get(
        "/api/v1/overview"
    )

    data = response.get_json()

    names = [
        obj["name"]
        for obj in data["objects"]
    ]

    assert "Earth" in names

def test_analysis_api():

    client = app.test_client()

    response = client.post(
        "/api/v1/analysis",
        json={
            "reference": "earth",
            "target": "jupiter",
            "start_date": "2026-08-23",
            "months": 1,
            "interval_days": 7,
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["reference"] == "Earth"
    assert data["target"] == "Jupiter"

    assert "results" in data

    assert len(data["results"]) > 0


def test_analysis_api_invalid_body():

    client = app.test_client()

    response = client.post(
        "/api/v1/analysis",
        json={
            "reference": "earth",
            "target": "not-a-planet",
            "start_date": "2026-08-23",
            "months": 1,
            "interval_days": 7,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "Invalid target body."
    )

def test_analysis_api_invalid_months():

    client = app.test_client()

    response = client.post(
        "/api/v1/analysis",
        json={
            "reference": "earth",
            "target": "jupiter",
            "start_date": "2026-08-23",
            "months": 0,
            "interval_days": 7,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "months must be greater than zero."
    )


def test_analysis_api_invalid_interval():

    client = app.test_client()

    response = client.post(
        "/api/v1/analysis",
        json={
            "reference": "earth",
            "target": "jupiter",
            "start_date": "2026-08-23",
            "months": 1,
            "interval_days": 0,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == (
        "interval_days must be greater than zero."
    )