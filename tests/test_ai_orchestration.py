from astrosphere.ai import (
    AIOrchestrationRequest,
    AIOrchestrationResult,
    orchestrate_ai_request,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def test_orchestrate_single_capability(monkeypatch):
    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="What is Earth's scientific state?",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    result = orchestrate_ai_request(request)

    assert isinstance(
        result,
        AIOrchestrationResult,
    )
    assert result.question == (
        "What is Earth's scientific state?"
    )
    assert result.object_id == "earth"
    assert result.capabilities == (
        "scientific-data",
    )
    assert len(result.results) == 1
    assert result.results[0].capability_id == (
        "scientific-data"
    )


def test_orchestrate_multiple_capabilities(monkeypatch):
    executed = []

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        executed.append(capability_id)

        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="Analyze Apophis.",
        object_id="asteroid:99942",
        capability_ids=(
            "scientific-data",
            "tracking",
            "close-approaches",
        ),
    )

    result = orchestrate_ai_request(request)

    assert executed == [
        "scientific-data",
        "tracking",
        "close-approaches",
    ]

    assert result.capabilities == (
        "scientific-data",
        "tracking",
        "close-approaches",
    )
    assert len(result.results) == 3


def test_orchestrate_normalizes_capability_ids(monkeypatch):
    executed = []

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        executed.append(capability_id)

        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="Check space weather.",
        object_id="earth",
        capability_ids=(
            " SPACE-WEATHER ",
        ),
    )

    result = orchestrate_ai_request(request)

    assert executed == ["space-weather"]
    assert result.capabilities == (
        "space-weather",
    )


def test_orchestrate_rejects_unavailable_capability():
    request = AIOrchestrationRequest(
        question="Show Earth's trajectory.",
        object_id="earth",
        capability_ids=("trajectory",),
    )

    try:
        orchestrate_ai_request(request)
    except ValueError as exc:
        assert "not available" in str(exc)
    else:
        raise AssertionError(
            "Expected unavailable capability to be rejected."
        )


def test_orchestrate_rejects_invalid_request():
    try:
        orchestrate_ai_request(object())
    except ValueError as exc:
        assert "AIOrchestrationRequest is required" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid request to be rejected."
        )


def test_orchestrate_uses_all_available_capabilities_when_unspecified(
    monkeypatch,
):
    executed = []

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        executed.append(capability_id)

        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="Inspect the Sun.",
        object_id="sun",
    )

    result = orchestrate_ai_request(request)

    assert executed == [
        "context",
        "relationships",
    ]

    assert result.capabilities == (
        "context",
        "relationships",
    )
