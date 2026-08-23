from web.app import app


def test_home_page():

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_overview_page():

    client = app.test_client()

    response = client.get("/overview")

    assert response.status_code == 200


def test_jupiter_planet_page():

    client = app.test_client()

    response = client.get(
        "/planet/jupiter"
    )

    assert response.status_code == 200


def test_mars_planet_page():

    client = app.test_client()

    response = client.get(
        "/planet/mars"
    )

    assert response.status_code == 200


def test_invalid_planet_page():

    client = app.test_client()

    response = client.get(
        "/planet/not-a-planet"
    )

    assert response.status_code == 200

    assert (
        b"Invalid planetary body"
        in response.data
    )


def test_analysis_page():

    client = app.test_client()

    response = client.post(
        "/analyze",
        data={
            "reference": "earth",
            "target": "jupiter",
            "start_date": "2020-01-01",
            "period": "3",
            "interval": "7",
        },
    )

    assert response.status_code == 200