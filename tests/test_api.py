from datetime import datetime, timezone

from web.app import app

from astrosphere.models.celestial import (
    CelestialObject,
)

from astrosphere.models.scientific import (
    ScientificData,
)

from astrosphere.models.scientific import (
    ScientificData,
)

def test_get_monitoring_status(monkeypatch):
    def fake_monitoring_status():
        return {
            "enabled": True,
            "healthy": True,
            "sources": [
                {
                    "source": "NASA/JPL CNEOS",
                    "healthy": True,
                    "checked_at": (
                        "2026-09-26T04:00:00+00:00"
                    ),
                    "last_success_at": (
                        "2026-09-26T04:00:00+00:00"
                    ),
                    "last_data_at": (
                        "2026-09-26T04:00:00+00:00"
                    ),
                    "error": None,
                }
            ],
        }

    monkeypatch.setattr(
        "web.api.get_monitoring_status",
        fake_monitoring_status,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/monitoring/status"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["enabled"] is True
    assert data["data"]["healthy"] is True
    assert len(data["data"]["sources"]) == 1

    source = data["data"]["sources"][0]

    assert source["source"] == "NASA/JPL CNEOS"
    assert source["healthy"] is True
    assert source["error"] is None

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

def test_get_celestial_object_context_earth(
    monkeypatch,
):

    def fake_context(object_id, observation_time=None):

        assert object_id == "earth"

        return {
            "object": CelestialObject(
                id="earth",
                name="Earth",
                object_type="planet",
                parent_id="sun",
                system_id="solar-system",
            ),
            "parent": CelestialObject(
                id="sun",
                name="Sun",
                object_type="star",
                parent_id="solar-system",
                system_id="solar-system",
            ),
            "system": CelestialObject(
                id="solar-system",
                name="Solar System",
                object_type="system",
            ),
            "ancestors": [
                CelestialObject(
                    id="sun",
                    name="Sun",
                    object_type="star",
                    parent_id="solar-system",
                    system_id="solar-system",
                ),
                CelestialObject(
                    id="solar-system",
                    name="Solar System",
                    object_type="system",
                ),
            ],
            "children": [
                CelestialObject(
                    id="spacecraft:25544",
                    name="ISS",
                    object_type="spacecraft",
                    parent_id="earth",
                    system_id="solar-system",
                ),
            ],
            "scientific_data": ScientificData(
    object_id=object_id,
),
        }

    monkeypatch.setattr(
        "web.api.get_celestial_object_context",
        fake_context,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/context"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == "earth"
    assert data["data"]["parent"]["id"] == "sun"
    assert len(data["data"]["ancestors"]) == 2
    assert data["data"]["children"][0]["id"] == (
        "spacecraft:25544"
    )
    assert data["data"]["scientific_data"] is not None


def test_get_celestial_object_context_apophis(
    monkeypatch,
):

    def fake_context(object_id, observation_time=None):

        assert object_id == "asteroid:99942"

        return {
            "object": CelestialObject(
                id="asteroid:99942",
                name="Apophis",
                object_type="asteroid",
                parent_id="solar-system",
                system_id="solar-system",
            ),
            "parent": CelestialObject(
                id="solar-system",
                name="Solar System",
                object_type="system",
            ),
            "system": CelestialObject(
                id="solar-system",
                name="Solar System",
                object_type="system",
            ),
            "ancestors": [
                CelestialObject(
                    id="solar-system",
                    name="Solar System",
                    object_type="system",
                ),
            ],
            "children": [],
            "scientific_data": ScientificData(
    object_id=object_id,
),
        }

    monkeypatch.setattr(
        "web.api.get_celestial_object_context",
        fake_context,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/asteroid:99942/context"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == (
        "asteroid:99942"
    )
    assert data["data"]["object"]["name"] == (
        "Apophis"
    )
    assert data["data"]["parent"]["id"] == (
        "solar-system"
    )
    assert data["data"]["children"] == []
    assert data["data"]["scientific_data"] is not None


def test_get_celestial_object_context_iss(
    monkeypatch,
):

    def fake_context(object_id, observation_time=None):

        assert object_id == "spacecraft:25544"

        return {
            "object": CelestialObject(
                id="spacecraft:25544",
                name="ISS",
                object_type="spacecraft",
                parent_id="earth",
                system_id="solar-system",
            ),
            "parent": CelestialObject(
                id="earth",
                name="Earth",
                object_type="planet",
                parent_id="sun",
                system_id="solar-system",
            ),
            "system": CelestialObject(
                id="solar-system",
                name="Solar System",
                object_type="system",
            ),
            "ancestors": [
                CelestialObject(
                    id="earth",
                    name="Earth",
                    object_type="planet",
                    parent_id="sun",
                    system_id="solar-system",
                ),
                CelestialObject(
                    id="sun",
                    name="Sun",
                    object_type="star",
                    parent_id="solar-system",
                    system_id="solar-system",
                ),
                CelestialObject(
                    id="solar-system",
                    name="Solar System",
                    object_type="system",
                ),
            ],
            "children": [],
            "scientific_data": ScientificData(
    object_id=object_id,
),
        }

    monkeypatch.setattr(
        "web.api.get_celestial_object_context",
        fake_context,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/spacecraft:25544/context"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == (
        "spacecraft:25544"
    )
    assert data["data"]["parent"]["id"] == "earth"
    assert len(data["data"]["ancestors"]) == 3
    assert data["data"]["scientific_data"] is not None


def test_get_celestial_object_context_unknown():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/not-real/context"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert "error" in data


def test_get_celestial_object_context_invalid_time():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/context"
        "?observation_time=not-a-date"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "error" in data

def test_get_celestial_object_capabilities_earth():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/capabilities"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == "earth"
    assert data["data"]["count"] == 6

    capability_ids = {
        capability["id"]
        for capability in data["data"]["capabilities"]
    }

    assert capability_ids == {
        "context",
        "scientific-data",
        "relationships",
        "space-weather",
        "orbital-analysis",
        "planetary-trajectory",
    }


def test_get_celestial_object_capabilities_apophis():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/asteroid:99942/capabilities"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == "asteroid:99942"
    assert data["data"]["count"] == 6

    capability_ids = {
        capability["id"]
        for capability in data["data"]["capabilities"]
    }

    assert capability_ids == {
        "context",
        "scientific-data",
        "relationships",
        "tracking",
        "trajectory",
        "close-approaches",
    }


def test_get_celestial_object_capabilities_iss():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/spacecraft:25544/capabilities"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == "spacecraft:25544"
    assert data["data"]["count"] == 4

    capability_ids = {
        capability["id"]
        for capability in data["data"]["capabilities"]
    }

    assert capability_ids == {
        "context",
        "scientific-data",
        "relationships",
        "tracking",
    }


def test_get_celestial_object_capabilities_sun():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/sun/capabilities"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object"]["id"] == "sun"
    assert data["data"]["count"] == 3

    capability_ids = {
        capability["id"]
        for capability in data["data"]["capabilities"]
    }

    assert capability_ids == {
        "context",
        "scientific-data",
        "relationships",
    }


def test_get_celestial_object_capabilities_unknown():

    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/not-real/capabilities"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert "error" in data
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def test_execute_capability_success(monkeypatch):

    def fake_execute(request):

        assert request.object_id == "earth"
        assert request.capability_id == "relationships"

        return CapabilityExecutionResult(
            object_id="earth",
            capability_id="relationships",
            result={
                "parent": "sun",
                "children": ["spacecraft:25544"],
            },
            metadata={
                "source": "test",
            },
        )

    monkeypatch.setattr(
        "web.api.execute_capability",
        fake_execute,
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "earth",
            "capability_id": "relationships",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object_id"] == "earth"
    assert data["data"]["capability_id"] == "relationships"
    assert data["data"]["result"]["parent"] == "sun"
    assert data["data"]["metadata"]["source"] == "test"


def test_execute_capability_rejects_invalid_body():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["error"]
        == "Request body must be a JSON object."
    )


def test_execute_capability_requires_fields():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "Object ID is required."


def test_execute_capability_rejects_unsupported_capability():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "sun",
            "capability_id": "trajectory",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "not supported" in data["error"]
def test_execute_capability_requires_capability_id():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "earth",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "Capability ID is required."


def test_execute_capability_rejects_unknown_object():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "not-real",
            "capability_id": "context",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "Unknown celestial object" in data["error"]


def test_execute_capability_rejects_invalid_parameters():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "asteroid:99942",
            "capability_id": "trajectory",
            "parameters": {
                "samples": "not-an-integer",
            },
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "integer" in data["error"]


def test_execute_capability_rejects_unexpected_parameters():

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "earth",
            "capability_id": "relationships",
            "parameters": {
                "unexpected": True,
            },
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "Unsupported parameters" in data["error"]


def test_execute_capability_accepts_parameters(monkeypatch):

    captured = {}

    def fake_execute(execution_request):

        captured["request"] = execution_request

        return CapabilityExecutionResult(
            object_id="asteroid:99942",
            capability_id="trajectory",
            result={"samples": 2200},
        )

    monkeypatch.setattr(
        "web.api.execute_capability",
        fake_execute,
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/capabilities/execute",
        json={
            "object_id": "asteroid:99942",
            "capability_id": "trajectory",
            "parameters": {
                "samples": 2200,
            },
        },
    )

    assert response.status_code == 200

    request_object = captured["request"]

    assert request_object.object_id == "asteroid:99942"
    assert request_object.capability_id == "trajectory"
    assert request_object.parameters == {
        "samples": 2200,
    }



def test_get_planetary_trajectory(monkeypatch):

    captured = {}

    def fake_trajectory(
        planet_name,
        observation_time=None,
        days=365,
        samples=181,
    ):

        captured["planet_name"] = planet_name
        captured["observation_time"] = observation_time
        captured["days"] = days
        captured["samples"] = samples

        return [
            {
                "date": datetime(2026, 9, 19, tzinfo=timezone.utc),
                "x_au": 1.0,
                "y_au": 0.0,
                "z_au": 0.0,
            },
            {
                "date": datetime(2026, 10, 19, tzinfo=timezone.utc),
                "x_au": 0.9,
                "y_au": 0.4,
                "z_au": 0.0,
            },
        ]

    monkeypatch.setattr(
        "web.api.calculate_planetary_trajectory",
        fake_trajectory,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/earth/trajectory"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert data["data"]["object_id"] == "earth"
    assert data["data"]["name"] == "Earth"
    assert data["data"]["days"] == 365

    assert len(data["data"]["samples"]) == 2

    assert (
        data["data"]["samples"][0]["x_au"]
        == 1.0
    )

    assert (
        data["data"]["samples"][1]["y_au"]
        == 0.4
    )

    assert captured["planet_name"] == "earth"
    assert captured["days"] == 365
    assert captured["samples"] == 181


def test_get_planetary_trajectory_accepts_parameters(
    monkeypatch,
):

    captured = {}

    def fake_trajectory(
        planet_name,
        observation_time=None,
        days=365,
        samples=181,
    ):

        captured["planet_name"] = planet_name
        captured["observation_time"] = observation_time
        captured["days"] = days
        captured["samples"] = samples

        return [
            {
                "date": datetime(2026, 9, 19, tzinfo=timezone.utc),
                "x_au": 1.0,
                "y_au": 0.0,
                "z_au": 0.0,
            }
        ]

    monkeypatch.setattr(
        "web.api.calculate_planetary_trajectory",
        fake_trajectory,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/earth/trajectory"
        "?days=30"
        "&samples=5"
        "&observation_time="
        "2026-09-19T12:00:00%2B00:00"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object_id"] == "earth"
    assert data["data"]["days"] == 30
    assert len(data["data"]["samples"]) == 1

    assert captured["planet_name"] == "earth"
    assert captured["days"] == 30
    assert captured["samples"] == 5

    assert (
        captured["observation_time"].isoformat()
        == "2026-09-19T12:00:00+00:00"
    )


def test_get_planetary_trajectory_rejects_invalid_planet():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/pluto-like-object/trajectory"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == (
        "Invalid planetary body."
    )


def test_get_planetary_trajectory_rejects_invalid_parameters():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/earth/trajectory"
        "?days=not-an-integer"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "days and samples must be integers" in (
        data["error"]
    )


def test_get_planetary_trajectory_rejects_invalid_observation_time():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/earth/trajectory"
        "?observation_time=not-a-date"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "Invalid observation_time" in (
        data["error"]
    )


def test_get_planetary_trajectory_rejects_invalid_days():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/earth/trajectory"
        "?days=0"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "days must be at least 1" in (
        data["error"]
    )


def test_get_planetary_trajectory_rejects_invalid_samples():

    client = app.test_client()

    response = client.get(
        "/api/v1/planets/earth/trajectory"
        "?samples=1"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert "samples must be at least 2" in (
        data["error"]
    )








def test_get_celestial_object_graph_earth():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/earth/graph"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["id"] == "earth"
    assert data["name"] == "Earth"
    assert data["object_type"] == "planet"

    assert data["parent"]["id"] == "sun"

    assert [
        ancestor["id"]
        for ancestor in data["ancestors"]
    ] == [
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]

    assert {
        child["id"]
        for child in data["children"]
    } == {
        "moon",
        "spacecraft:25544",
    }

    assert {
        (
            relationship["source_id"],
            relationship["relationship_type"],
            relationship["target_id"],
        )
        for relationship in data["relationships"]
    } == {
        ("earth", "orbits", "sun"),
        ("earth", "contains", "moon"),
        ("earth", "contains", "spacecraft:25544"),
    }


def test_get_celestial_object_graph_milky_way():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/milky-way/graph"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["id"] == "milky-way"
    assert data["parent"]["id"] == "universe"

    assert {
        child["id"]
        for child in data["children"]
    } == {
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    }


def test_get_celestial_object_graph_leaf_object():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/sirius/graph"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["id"] == "sirius"
    assert data["parent"]["id"] == "milky-way"
    assert data["children"] == []


def test_get_celestial_object_graph_unknown_object():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/not-a-real-object/graph"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "Celestial object was not found."

def test_get_celestial_object_ancestors_earth():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/ancestors"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "earth"
    assert data["data"]["name"] == "Earth"

    assert data["data"]["ancestors"] == [
        {
            "id": "sun",
            "name": "Sun",
            "object_type": "star",
        },
        {
            "id": "solar-system",
            "name": "Solar System",
            "object_type": "system",
        },
        {
            "id": "milky-way",
            "name": "Milky Way",
            "object_type": "galaxy",
        },
        {
            "id": "universe",
            "name": "Universe",
            "object_type": "universe",
        },
    ]


def test_get_celestial_object_ancestors_universe():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/universe/ancestors"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "universe"
    assert data["data"]["name"] == "Universe"
    assert data["data"]["ancestors"] == []


def test_get_celestial_object_ancestors_sirius():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/sirius/ancestors"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "sirius"
    assert data["data"]["name"] == "Sirius"

    assert data["data"]["ancestors"] == [
        {
            "id": "milky-way",
            "name": "Milky Way",
            "object_type": "galaxy",
        },
        {
            "id": "universe",
            "name": "Universe",
            "object_type": "universe",
        },
    ]


def test_get_celestial_object_ancestors_unknown_object():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/not-a-real-object/ancestors"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "Celestial object was not found."


def test_get_celestial_object_children_earth():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/children"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "earth"
    assert data["data"]["name"] == "Earth"

    assert data["data"]["children"] == [
        {
            "id": "moon",
            "name": "Moon",
            "object_type": "moon",
        },
        {
            "id": "spacecraft:25544",
            "name": "ISS",
            "object_type": "spacecraft",
        },
    ]


def test_get_celestial_object_children_milky_way():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/milky-way/children"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "milky-way"
    assert data["data"]["name"] == "Milky Way"

    assert data["data"]["children"] == [
        {
            "id": "solar-system",
            "name": "Solar System",
            "object_type": "system",
        },
        {
            "id": "sirius",
            "name": "Sirius",
            "object_type": "star",
        },
        {
            "id": "proxima-centauri",
            "name": "Proxima Centauri",
            "object_type": "star",
        },
        {
            "id": "betelgeuse",
            "name": "Betelgeuse",
            "object_type": "star",
        },
        {
            "id": "vega",
            "name": "Vega",
            "object_type": "star",
        },
    ]


def test_get_celestial_object_children_leaf_object():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/sirius/children"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "sirius"
    assert data["data"]["name"] == "Sirius"
    assert data["data"]["children"] == []


def test_get_celestial_object_children_unknown_object():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/not-a-real-object/children"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "Celestial object was not found."


def test_get_celestial_object_relationships_earth():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "earth"
    assert data["data"]["name"] == "Earth"

    assert data["data"]["parent"]["id"] == "sun"

    relationships = data["data"]["relationships"]

    assert relationships[0] == {
        "source_id": "earth",
        "relationship_type": "orbits",
        "target_id": "sun",
    }

    assert [
        relationship["target_id"]
        for relationship in relationships
        if relationship["relationship_type"] == "contains"
    ] == [
        "moon",
        "spacecraft:25544",
    ]


def test_get_celestial_object_relationships_filter_contains():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/relationships?relationship_type=contains"
    )

    assert response.status_code == 200

    data = response.get_json()
    relationships = data["data"]["relationships"]

    assert relationships == [
        {
            "source_id": "earth",
            "relationship_type": "contains",
            "target_id": "moon",
        },
        {
            "source_id": "earth",
            "relationship_type": "contains",
            "target_id": "spacecraft:25544",
        },
    ]


def test_get_celestial_object_relationships_filter_orbits():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/relationships?relationship_type=orbits"
    )

    assert response.status_code == 200

    data = response.get_json()
    relationships = data["data"]["relationships"]

    assert relationships == [
        {
            "source_id": "earth",
            "relationship_type": "orbits",
            "target_id": "sun",
        },
    ]


def test_get_celestial_object_relationships_filter_is_case_insensitive():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/relationships?relationship_type=CONTAINS"
    )

    assert response.status_code == 200

    data = response.get_json()
    relationships = data["data"]["relationships"]

    assert [
        relationship["target_id"]
        for relationship in relationships
    ] == [
        "moon",
        "spacecraft:25544",
    ]


def test_get_celestial_object_relationships_iss():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/spacecraft:25544/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "spacecraft:25544"

    assert data["data"]["relationships"] == [
        {
            "source_id": "spacecraft:25544",
            "relationship_type": "orbits",
            "target_id": "earth",
        }
    ]


def test_get_celestial_object_relationships_apophis():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/asteroid:99942/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "asteroid:99942"
    assert data["data"]["name"] == "Apophis"

    assert data["data"]["relationships"] == [
        {
            "source_id": "asteroid:99942",
            "relationship_type": "orbits",
            "target_id": "sun",
        }
    ]


def test_get_celestial_object_relationships_sun_includes_orbiting_objects():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/sun/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["id"] == "sun"

    assert [
        relationship["target_id"]
        for relationship in data["data"]["relationships"]
        if relationship["relationship_type"] == "contains"
    ] == [
        "mercury",
        "venus",
        "earth",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]

    assert {
        child["id"]
        for child in data["data"]["children"]
    } >= {
        "mercury",
        "venus",
        "earth",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    }


def test_get_celestial_object_relationships_unknown():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/not-real/relationships"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert "error" in data
def test_get_celestial_object_relationships_moon():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/moon/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["id"] == "moon"
    assert data["name"] == "Moon"
    assert data["parent"]["id"] == "earth"

    assert {
        relationship["relationship_type"]
        for relationship in data["relationships"]
    } == {
        "orbits",
    }

    assert data["relationships"][0]["target_id"] == "earth"


def test_get_celestial_object_relationships_phobos():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/phobos/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert data["parent"]["id"] == "mars"
    assert data["relationships"][0]["target_id"] == "mars"


def test_get_celestial_object_relationships_jupiter_moons():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/jupiter/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    child_ids = {
        child["id"]
        for child in data["children"]
    }

    assert child_ids == {
        "io",
        "europa",
        "ganymede",
        "callisto",
    }


def test_get_celestial_object_relationships_saturn_moons():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/saturn/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    child_ids = {
        child["id"]
        for child in data["children"]
    }

    assert child_ids == {
        "titan",
        "enceladus",
    }


def test_get_celestial_object_relationships_uranus_moons():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/uranus/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    child_ids = {
        child["id"]
        for child in data["children"]
    }

    assert child_ids == {
        "miranda",
        "titania",
        "oberon",
    }


def test_get_celestial_object_relationships_neptune_moon():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/neptune/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    child_ids = {
        child["id"]
        for child in data["children"]
    }

    assert child_ids == {
        "triton",
    }


def test_get_celestial_object_relationships_pluto_moon():
    client = app.test_client()
    response = client.get(
        "/api/v1/celestial-objects/pluto/relationships"
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    child_ids = {
        child["id"]
        for child in data["children"]
    }

    assert child_ids == {
        "charon",
    }

# =========================================================
# Monitoring API
# =========================================================

def test_get_monitoring_events(monkeypatch):
    def fake_events(**kwargs):
        assert kwargs["limit"] == 10
        assert kwargs["severity"] == "warning"
        assert kwargs["source"] == "NASA/JPL CNEOS"

        return [
            {
                "event_id": "event-001",
                "event_type": "asteroid_close_approach",
                "source": "NASA/JPL CNEOS",
                "detected_at": "2026-09-26T04:00:00+00:00",
                "event_time": None,
                "object_id": "asteroid:2026 SA8",
                "object_name": "(2026 SA8)",
                "affected_body": "Earth",
                "severity": "warning",
                "status": "active",
                "summary": (
                    "(2026 SA8) has a recorded Earth "
                    "close approach."
                ),
                "source_url": (
                    "https://ssd-api.jpl.nasa.gov/cad.api"
                ),
                "data": {},
                "fingerprint": "fingerprint-001",
            }
        ]

    monkeypatch.setattr(
        "web.api.list_monitoring_events",
        fake_events,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/monitoring/events"
        "?limit=10"
        "&severity=warning"
        "&source=NASA/JPL%20CNEOS"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["count"] == 1

    event = data["data"]["events"][0]

    assert event["event_id"] == "event-001"
    assert event["severity"] == "warning"
    assert event["source"] == "NASA/JPL CNEOS"
    assert event["object_name"] == "(2026 SA8)"


def test_get_monitoring_events_rejects_invalid_limit():
    client = app.test_client()

    response = client.get(
        "/api/v1/monitoring/events?limit=invalid"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "limit must be an integer."


def test_get_monitoring_events_rejects_limit_out_of_range():
    client = app.test_client()

    response = client.get(
        "/api/v1/monitoring/events?limit=501"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["error"]
        == "limit must be between 1 and 500."
    )


def test_get_monitoring_alerts(monkeypatch):
    def fake_alerts(**kwargs):
        assert kwargs["limit"] == 10
        assert kwargs["acknowledged"] is False

        return [
            {
                "alert_id": "alert-001",
                "event_id": "event-001",
                "severity": "warning",
                "title": "WARNING: asteroid close approach",
                "message": (
                    "(2026 SA8) has a recorded Earth "
                    "close approach."
                ),
                "created_at": (
                    "2026-09-26T04:00:00+00:00"
                ),
                "acknowledged": False,
                "metadata": {
                    "source": "NASA/JPL CNEOS",
                    "object_id": "asteroid:2026 SA8",
                    "affected_body": "Earth",
                },
            }
        ]

    monkeypatch.setattr(
        "web.api.list_monitoring_alerts",
        fake_alerts,
    )

    client = app.test_client()

    response = client.get(
        "/api/v1/monitoring/alerts"
        "?limit=10"
        "&acknowledged=false"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["count"] == 1

    alert = data["data"]["alerts"][0]

    assert alert["alert_id"] == "alert-001"
    assert alert["event_id"] == "event-001"
    assert alert["severity"] == "warning"
    assert alert["acknowledged"] is False


def test_get_monitoring_alerts_rejects_invalid_acknowledged():
    client = app.test_client()

    response = client.get(
        "/api/v1/monitoring/alerts"
        "?acknowledged=maybe"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["error"]
        == "acknowledged must be true or false."
    )


def test_acknowledge_monitoring_alert(monkeypatch):
    def fake_acknowledge(alert_id):
        assert alert_id == "alert-001"
        return True

    monkeypatch.setattr(
        "web.api.acknowledge_monitoring_alert",
        fake_acknowledge,
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/monitoring/alerts/alert-001/acknowledge"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert (
        data["data"]["alert_id"]
        == "alert-001"
    )
    assert data["data"]["acknowledged"] is True


def test_acknowledge_monitoring_alert_not_found(
    monkeypatch,
):
    def fake_acknowledge(alert_id):
        assert alert_id == "missing-alert"
        return False

    monkeypatch.setattr(
        "web.api.acknowledge_monitoring_alert",
        fake_acknowledge,
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/monitoring/alerts/missing-alert/acknowledge"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["error"]
        == "Monitoring alert not found."
    )
