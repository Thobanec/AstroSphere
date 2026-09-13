from web.app import app

def test_get_spacecraft_tracking(
    monkeypatch,
):

    def fake_tracker(norad_id):

        return {
            "name": "ISS (ZARYA)",
            "observation_time": (
                "2024-05-01T12:00:00+00:00"
            ),
            "position_km": {
                "x": 1000.0,
                "y": 2000.0,
                "z": 3000.0,
            },
            "velocity_km_s": {
                "x": 1.0,
                "y": 2.0,
                "z": 3.0,
            },
        }

    monkeypatch.setattr(
        "web.api.track_spacecraft_by_norad",
        fake_tracker,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/spacecraft/25544"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert (
        data["data"]["name"]
        == "ISS (ZARYA)"
    )

    assert (
        data["data"]["position_km"]["x"]
        == 1000.0
    )

    assert (
        data["data"]["velocity_km_s"]["x"]
        == 1.0
    )