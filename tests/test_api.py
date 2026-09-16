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
    assert data["data"]["count"] == 5

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
    assert data["data"]["count"] == 2

    capability_ids = {
        capability["id"]
        for capability in data["data"]["capabilities"]
    }

    assert capability_ids == {
        "context",
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
