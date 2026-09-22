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


def test_ai_query_returns_planetary_trajectory(monkeypatch):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "Show the trajectory of Earth.",
            "object_id": "earth",
            "parameters": {
                "days": 30,
                "samples": 5,
            },
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object_id"] == "earth"
    assert data["data"]["capabilities"] == [
        "planetary-trajectory",
    ]

    answer = data["data"]["answer"]

    assert "Earth trajectory:" in answer
    assert "Calculated from " in answer
    assert "Trajectory samples: 5." in answer
    assert "Reference frame: heliocentric ecliptic." in answer

    assert "Start position: (" in answer
    assert "End position: (" in answer
    assert " AU." in answer

    assert "trajectory_sample_count:" not in answer
    assert "trajectory_start_date:" not in answer
    assert "trajectory_end_date:" not in answer
    assert "trajectory_coordinate_frame:" not in answer
    assert "trajectory_start_x:" not in answer
    assert "trajectory_start_y:" not in answer
    assert "trajectory_start_z:" not in answer
    assert "trajectory_end_x:" not in answer
    assert "trajectory_end_y:" not in answer
    assert "trajectory_end_z:" not in answer

    assert data["data"]["provenance"]
    assert data["data"]["uncertainties"] == []

def test_ai_query_exposes_provenance_and_uncertainties(
    monkeypatch,
):
    from astrosphere.ai.orchestration import (
        AIOrchestrationResult,
    )
    from astrosphere.models.scientific import (
        DataSource,
    )

    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    result = AIOrchestrationResult(
        question="What is Earth?",
        object_id="earth",
        answer="Test response.",
        capabilities=("scientific-data",),
        provenance=(source,),
        uncertainties=(
            "Test uncertainty.",
        ),
    )

    monkeypatch.setattr(
        "web.api.orchestrate_ai_request",
        lambda request, language_provider=None: result,
    )

    monkeypatch.setattr(
        "web.api.create_language_provider",
        lambda: DeterministicLanguageProvider(),
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "What is Earth?",
            "object_id": "earth",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["provenance"] == [
        {
            "name": "Test Source",
            "provider": "Test Provider",
            "url": None,
            "dataset": "Test Dataset",
            "version": None,
            "upstream_source": None,
        }
    ]
    assert data["data"]["uncertainties"] == [
        "Test uncertainty.",
    ]


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
def test_ai_query_assistant_exposes_provenance_and_uncertainties(
    monkeypatch,
):
    from astrosphere.ai.orchestration import (
        AIOrchestrationResult,
    )
    from astrosphere.models.scientific import (
        DataSource,
    )

    source = DataSource(
        name="Assistant Source",
        provider="Assistant Provider",
        dataset="Assistant Dataset",
    )

    result = AIOrchestrationResult(
        question="Where is Earth?",
        object_id="earth",
        answer="Assistant response.",
        capabilities=("scientific-data",),
        provenance=(source,),
        uncertainties=(
            "Assistant uncertainty.",
        ),
    )

    monkeypatch.setattr(
        "web.api.process_assistant_message",
        lambda *args, **kwargs: (
            kwargs.get("_test_conversation"),
            result,
        ),
    )

    # Replace the assistant service with a deterministic
    # response while preserving the API serialization path.
    from astrosphere.ai.conversation import AIConversation

    conversation = AIConversation(
        conversation_id="conversation-metadata",
        messages=(),
        object_id="earth",
    )

    monkeypatch.setattr(
        "web.api.process_assistant_message",
        lambda *args, **kwargs: (
            conversation,
            result,
        ),
    )

    monkeypatch.setattr(
        "web.api.create_language_provider",
        lambda: DeterministicLanguageProvider(),
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "conversation_id": "conversation-metadata",
            "message": "Where is Earth?",
            "object_id": "earth",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["provenance"][0]["name"] == (
        "Assistant Source"
    )
    assert data["data"]["uncertainties"] == [
        "Assistant uncertainty.",
    ]


def test_ai_query_assistant_preserves_conversation_history(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        from astrosphere.capabilities.results import (
            CapabilityExecutionResult,
        )

        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "conversation_id": "conversation-001",
            "message": "How fast is it moving?",
            "messages": [
                {
                    "role": "user",
                    "content": "Where is Apophis?",
                    "object_id": "asteroid:99942",
                },
                {
                    "role": "assistant",
                    "content": "Apophis tracking data.",
                    "object_id": "asteroid:99942",
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["conversation_id"] == (
        "conversation-001"
    )
    assert data["data"]["object_id"] == (
        "asteroid:99942"
    )

    messages = data["data"]["messages"]

    assert len(messages) == 4
    assert messages[0]["content"] == "Where is Apophis?"
    assert messages[0]["object_id"] == "asteroid:99942"
    assert messages[1]["content"] == (
        "Apophis tracking data."
    )
    assert messages[2]["content"] == (
        "How fast is it moving?"
    )
    assert messages[2]["object_id"] == (
        "asteroid:99942"
    )
    assert messages[3]["role"] == "assistant"


def test_ai_query_assistant_requires_conversation_id():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "message": "Where is Earth?",
            "object_id": "earth",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == (
        "conversation_id is required "
        "for assistant messages."
    )


def test_ai_query_assistant_rejects_invalid_messages():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "conversation_id": "conversation-002",
            "message": "Where is Earth?",
            "object_id": "earth",
            "messages": "invalid",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == (
        "messages must be a list."
    )


def test_ai_query_assistant_rejects_malformed_message():
    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "conversation_id": "conversation-003",
            "message": "Where is Earth?",
            "object_id": "earth",
            "messages": [
                {
                    "role": "user",
                }
            ],
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == (
        "conversation messages require "
        "role and content."
    )

def test_celestial_object_ai_context_endpoint():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/ai-context"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["status"] == "success"
    assert payload["data"]["object"]["id"] == "earth"
    assert payload["data"]["object"]["name"] == "Earth"
    assert payload["data"]["scientific_data"] is not None
    assert payload["data"]["capabilities"]
    assert payload["data"]["object_graph"] is not None


def test_celestial_object_ai_context_endpoint_supports_question():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/sirius/ai-context",
        query_string={
            "question": "What is Sirius?"
        },
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["status"] == "success"
    assert payload["data"]["question"] == "What is Sirius?"
    assert payload["data"]["object"]["id"] == "sirius"
    assert payload["data"]["scientific_data"] is not None
    assert payload["data"]["provenance"]


def test_celestial_object_ai_context_endpoint_supports_observation_time():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/earth/ai-context",
        query_string={
            "observation_time": "2026-09-21T12:00:00Z"
        },
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["status"] == "success"
    assert (
        payload["data"]["observation_time"]
        == "2026-09-21T12:00:00+00:00"
    )


def test_celestial_object_ai_context_milky_way_includes_stars():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/milky-way/ai-context"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["status"] == "success"

    children = payload["data"]["object_graph"]["children"]
    child_ids = {
        child["id"]
        for child in children
    }

    assert {
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    } <= child_ids


def test_celestial_object_ai_context_unknown_object():
    client = app.test_client()

    response = client.get(
        "/api/v1/celestial-objects/unknown-object/ai-context"
    )

    assert response.status_code == 404

    payload = response.get_json()

    assert payload["status"] == "error"
    assert (
        payload["error"]
        == "Unknown celestial object: unknown-object"
    )

def test_celestial_capability_execution_endpoint_scientific_data():
    client = app.test_client()

    response = client.post(
        "/api/v1/celestial-objects/earth/capabilities/"
        "scientific-data/execute",
        json={},
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["data"]["object_id"] == "earth"
    assert data["data"]["capability_id"] == "scientific-data"

    result = data["data"]["result"]

    assert result["object_id"] == "earth"
    assert result["physical_properties"] is not None
    assert result["provenance"] is not None


def test_celestial_capability_execution_endpoint_serializes_trajectory_dates():
    client = app.test_client()

    response = client.post(
        "/api/v1/celestial-objects/earth/capabilities/"
        "planetary-trajectory/execute",
        json={
            "parameters": {
                "days": 5,
                "samples": 5,
            }
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    result = data["data"]["result"]

    assert isinstance(result, list)
    assert len(result) == 5

    assert isinstance(result[0]["date"], str)
    assert "T" in result[0]["date"]
    assert "x_au" in result[0]
    assert "y_au" in result[0]
    assert "z_au" in result[0]


def test_celestial_capability_execution_endpoint_rejects_invalid_parameters():
    client = app.test_client()

    response = client.post(
        "/api/v1/celestial-objects/earth/capabilities/"
        "scientific-data/execute",
        json={
            "parameters": [],
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "parameters must be an object."


def test_celestial_capability_execution_endpoint_rejects_invalid_observation_time():
    client = app.test_client()

    response = client.post(
        "/api/v1/celestial-objects/earth/capabilities/"
        "scientific-data/execute",
        json={
            "observation_time": 12345,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"] == "observation_time must be a string."


def test_celestial_capability_execution_endpoint_rejects_unknown_capability():
    client = app.test_client()

    response = client.post(
        "/api/v1/celestial-objects/earth/capabilities/"
        "does-not-exist/execute",
        json={},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["error"]

def test_ai_query_serializes_planetary_trajectory_results(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "Show the trajectory of Earth.",
            "object_id": "earth",
            "parameters": {
                "days": 5,
                "samples": 5,
            },
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    results = data["data"]["results"]

    assert results

    trajectory_result = next(
        result
        for result in results
        if result["capability_id"] == "planetary-trajectory"
    )

    assert trajectory_result["object_id"] == "earth"

    assert isinstance(
        trajectory_result["result"],
        list,
    )

    assert len(trajectory_result["result"]) == 5

    first_sample = trajectory_result["result"][0]

    assert isinstance(first_sample["date"], str)

    assert first_sample["date"]

    assert isinstance(first_sample["x_au"], float)
    assert isinstance(first_sample["y_au"], float)
    assert isinstance(first_sample["z_au"], float)

def test_ai_query_serializes_multiple_capability_results(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "Analyze Earth scientifically and show its relationships.",
            "object_id": "earth",
            "capability_ids": [
                "scientific-data",
                "relationships",
            ],
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    payload = data["data"]

    assert payload["object_id"] == "earth"

    assert payload["capabilities"] == [
        "scientific-data",
        "relationships",
    ]

    results = payload["results"]

    assert len(results) == 2

    assert [
        result["capability_id"]
        for result in results
    ] == [
        "scientific-data",
        "relationships",
    ]

    for result in results:
        assert result["object_id"] == "earth"
        assert result["result"] is not None

    scientific_result = results[0]["result"]

    assert scientific_result["object_id"] == "earth"
    assert scientific_result["physical_properties"] is not None

    relationship_result = results[1]["result"]

    assert "object" in relationship_result
    assert relationship_result["object"]["id"] == "earth"

def test_ai_query_serializes_facts_and_interpretations(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": "Analyze Earth scientifically.",
            "object_id": "earth",
            "capability_ids": [
                "scientific-data",
            ],
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    payload = data["data"]

    assert payload["object_id"] == "earth"

    assert payload["facts"] is not None
    assert payload["facts"]["object_id"] == "earth"
    assert isinstance(
        payload["facts"]["facts"],
        list,
    )
    assert payload["facts"]["facts"]

    fact = payload["facts"]["facts"][0]

    assert "name" in fact
    assert "value" in fact
    assert "unit" in fact
    assert "source_capability" in fact

    assert payload["interpretations"] is not None
    assert payload["interpretations"]["object_id"] == "earth"
    assert isinstance(
        payload["interpretations"]["interpretations"],
        list,
    )
    assert payload["interpretations"]["interpretations"]

    interpretation = (
        payload["interpretations"]["interpretations"][0]
    )

    assert "subject" in interpretation
    assert "statement" in interpretation
    assert "supporting_facts" in interpretation
    assert "supporting_capabilities" in interpretation


def test_ai_query_handles_apophis_multi_capability_scenario(
    monkeypatch,
):
    import json

    class FakeMpcResponse:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            payload = [
                {
                    "mpc_orb": [
                        {
                            "designation_data": {
                                "iau_designation": "99942",
"name": "Apophis",
                                "permid": "99942",
                                "unpacked_primary_provisional_designation": (
                                    "2004 MN4"
                                ),
                                "orbfit_name": "99942",
                            },
                            "epoch_data": {
                                "epoch": 60400.0,
                                "timesystem": "TDB",
                            },
                            "COM": {
                                "coefficient_names": [
                                    "q",
                                    "e",
                                    "i",
                                    "node",
                                    "argperi",
                                    "peri_time",
                                        "yarkovski",
                                ],
                                "coefficient_values": [
                                    0.746076476674633,
                                    0.191290723544696,
                                    3.3397362277631,
                                    203.9153733183906,
                                    126.6832280492664,
                                    60395.3041068989,
                                        0.0,
                                ],
                            },
                        }
                    ]
                }
            ]

            return json.dumps(payload).encode("utf-8")

    def fake_mpc_urlopen(request, timeout):
        return FakeMpcResponse()

    monkeypatch.setattr(
        "astrosphere.astronomy.asteroids.urlopen",
        fake_mpc_urlopen,
    )

    class FakeCneosResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def read(self):
            payload = {
                "fields": [
                    "des",
                    "orbit_id",
                    "jd",
                    "cd",
                    "dist",
                    "dist_min",
                    "dist_max",
                    "v_rel",
                    "fullname",
                ],
                "data": [
                    [
                        "99942",
                        "123",
                        "2462247.5",
                        "2029-Apr-13 21:46",
                        "0.000254",
                        "0.000245",
                        "0.000263",
                        "5.86",
                        "99942 Apophis (2004 MN4)",
                    ],
                    [
                        "99942",
                        "123",
                        "2465162.5",
                        "2036-Apr-13 12:00",
                        "0.00031",
                        "0.00030",
                        "0.00032",
                        "5.80",
                        "99942 Apophis (2004 MN4)",
                    ],
                ],
            }

            return json.dumps(payload).encode("utf-8")

    def fake_cneos_urlopen(url, context=None, timeout=None):
        return FakeCneosResponse()

    monkeypatch.setattr(
        "astrosphere.scientific.close_approaches.urllib.request.urlopen",
        fake_cneos_urlopen,
    )

    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": (
                "What is Apophis's trajectory and what close approaches "
                "are known?"
            ),
            "object_id": "asteroid:99942",
            "parameters": {
                "samples": 5,
            },
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    payload = data["data"]

    assert payload["object_id"] == "asteroid:99942"

    assert "trajectory" in payload["capabilities"]
    assert "close-approaches" in payload["capabilities"]

    result_capabilities = [
        result["capability_id"]
        for result in payload["results"]
    ]

    assert "trajectory" in result_capabilities
    assert "close-approaches" in result_capabilities

    trajectory_result = next(
        result
        for result in payload["results"]
        if result["capability_id"] == "trajectory"
    )

    assert trajectory_result["object_id"] == "asteroid:99942"
    assert trajectory_result["result"] is not None

    close_approach_result = next(
        result
        for result in payload["results"]
        if result["capability_id"] == "close-approaches"
    )

    assert close_approach_result["object_id"] == "asteroid:99942"
    assert close_approach_result["result"] is not None

    assert payload["facts"]["object_id"] == "asteroid:99942"
    assert payload["facts"]["facts"]

    fact_capabilities = {
        fact["source_capability"]
        for fact in payload["facts"]["facts"]
        if fact["source_capability"] is not None
    }

    assert "trajectory" in fact_capabilities
    assert "close-approaches" in fact_capabilities

    assert payload["interpretations"]["object_id"] == "asteroid:99942"
    assert payload["interpretations"]["interpretations"]

    interpretation_capabilities = {
        capability
        for interpretation in payload["interpretations"]["interpretations"]
        for capability in interpretation["supporting_capabilities"]
    }

    assert "trajectory" in interpretation_capabilities
    assert "close-approaches" in interpretation_capabilities


def test_ai_query_handles_earth_orbital_analysis_scenario(monkeypatch):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": (
                "What are Earth's scientific properties and how does "
                "Earth move around the Sun?"
            ),
            "object_id": "earth",
            "parameters": {
                "reference_body": "sun",
                "target_body": "earth",
                "months": 1,
                "interval_days": 15,
            },
        },
    )

    assert response.status_code == 200

    payload = response.get_json()
    data = payload["data"]

    assert "scientific-data" in data["capabilities"]
    assert "orbital-analysis" in data["capabilities"]

    result_capabilities = {
        result["capability_id"]
        for result in data["results"]
    }

    assert "scientific-data" in result_capabilities
    assert "orbital-analysis" in result_capabilities

    scientific_result = next(
        result
        for result in data["results"]
        if result["capability_id"] == "scientific-data"
    )

    orbital_result = next(
        result
        for result in data["results"]
        if result["capability_id"] == "orbital-analysis"
    )

    assert scientific_result["result"] is not None
    assert orbital_result["result"] is not None

    facts = data["facts"]["facts"]

    assert any(
        fact["source_capability"] == "scientific-data"
        for fact in facts
    )

    assert any(
        fact["source_capability"] == "orbital-analysis"
        for fact in facts
    )

    interpretations = data["interpretations"]["interpretations"]

    assert any(
        "scientific-data" in interpretation["supporting_capabilities"]
        for interpretation in interpretations
    )

    assert any(
        "orbital-analysis" in interpretation["supporting_capabilities"]
        for interpretation in interpretations
    )


def test_ai_query_auto_selects_multiple_capabilities(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    client = app.test_client()

    response = client.post(
        "/api/v1/ai/query",
        json={
            "question": (
                "Where is Earth and what is its trajectory?"
            ),
            "object_id": "earth",
            "parameters": {
                "days": 5,
                "samples": 5,
            },
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    payload = data["data"]

    assert payload["object_id"] == "earth"

    assert payload["capabilities"]

    assert "scientific-data" in payload["capabilities"]
    assert "planetary-trajectory" in payload["capabilities"]

    results = payload["results"]

    assert results

    result_capabilities = [
        result["capability_id"]
        for result in results
    ]

    assert "scientific-data" in result_capabilities
    assert "planetary-trajectory" in result_capabilities

    trajectory_result = next(
        result
        for result in results
        if result["capability_id"]
        == "planetary-trajectory"
    )

    assert trajectory_result["object_id"] == "earth"

    assert isinstance(
        trajectory_result["result"],
        list,
    )

    assert len(trajectory_result["result"]) == 5

    first_sample = trajectory_result["result"][0]

    assert isinstance(
        first_sample["date"],
        str,
    )

    assert isinstance(
        first_sample["x_au"],
        float,
    )

    assert isinstance(
        first_sample["y_au"],
        float,
    )

    assert isinstance(
        first_sample["z_au"],
        float,
    )
