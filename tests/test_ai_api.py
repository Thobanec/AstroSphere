from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)

from web.app import app


def test_ai_query_returns_grounded_response(monkeypatch):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "What is the current position of Earth?",
            "object_id": "earth",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object_id"] == "earth"
    assert data["data"]["question"] == (
        "What is the current position of Earth?"
    )
    assert data["data"]["answer"]
    assert data["data"]["capabilities"]


def test_ai_query_requires_question():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "object_id": "earth",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "question is required."


def test_ai_query_requires_object_id():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "What is Earth?",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "object_id is required."


def test_ai_query_rejects_non_json():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        data="not-json",
        content_type="text/plain",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "JSON object is required."


def test_ai_query_rejects_invalid_capability_ids():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "What is Earth?",
            "object_id": "earth",
            "capability_ids": "scientific-data",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == (
        "capability_ids must be a list."
    )


def test_ai_query_rejects_invalid_parameters():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "What is Earth?",
            "object_id": "earth",
            "parameters": "invalid",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == (
        "parameters must be an object."
    )
