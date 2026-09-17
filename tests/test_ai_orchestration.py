from astrosphere.ai import (
    AICapabilityPlanItem,
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
    assert result.answer == (
        "AstroSphere retrieved the "
        "scientific-data result for Earth."
    )
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

    assert result.answer == (
        "AstroSphere retrieved the following "
        "capability results for Apophis: "
        "scientific-data, tracking, close-approaches."
    )

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


def test_orchestrate_executes_planner_output(monkeypatch):
    planned = (
        AICapabilityPlanItem(
            capability_id="relationships",
            reason="Test planner selection.",
            parameters={"test": True},
            execution_order=1,
        ),
    )

    executed = []

    def fake_plan(request):
        return planned

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        executed.append(
            (
                capability_id,
                parameters,
            )
        )

        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.plan_ai_capabilities",
        fake_plan,
    )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="Test planner authority.",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    result = orchestrate_ai_request(request)

    assert executed == [
        (
            "relationships",
            {"test": True},
        )
    ]

    assert result.answer == (
        "AstroSphere retrieved the "
        "relationships result for Earth."
    )

    assert result.capabilities == (
        "relationships",
    )

    assert len(result.results) == 1
    assert result.results[0].capability_id == (
        "relationships"
    )
def test_orchestrate_exposes_facts_and_interpretations(monkeypatch):
    from astrosphere.models.scientific import (
        Position,
        ScientificData,
        Velocity,
    )

    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=4.0,
            y=5.0,
            z=6.0,
            unit="AU/day",
            frame="ICRF",
        ),
    )

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result=scientific_data,
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="What is the current position of Earth?",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    result = orchestrate_ai_request(request)

    assert result.facts is not None
    assert result.facts.object_id == "earth"
    assert len(result.facts.facts) == 6

    assert result.interpretations is not None
    assert result.interpretations.object_id == "earth"
    assert len(result.interpretations.interpretations) == 6

    first = result.interpretations.interpretations[0]

    assert first.subject == "Earth"
    assert first.statement == (
        "Earth position_x is 1.0 AU."
    )
    assert first.supporting_facts == (
        "position_x",
    )
def test_orchestrate_preserves_interpretation_traceability(
    monkeypatch,
):
    from astrosphere.models.scientific import (
        Position,
        ScientificData,
        Velocity,
    )

    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=4.0,
            y=5.0,
            z=6.0,
            unit="AU/day",
            frame="ICRF",
        ),
    )

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result=scientific_data,
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="What is the current position of Earth?",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    result = orchestrate_ai_request(request)

    interpretation = (
        result.interpretations.interpretations[0]
    )

    assert interpretation.supporting_facts == (
        "position_x",
    )

    assert interpretation.supporting_capabilities == (
        "scientific-data",
    )
def test_orchestrate_preserves_fact_provenance(
    monkeypatch,
):
    from astrosphere.models.scientific import (
        DataSource,
        Position,
        ScientificData,
        ScientificProvenance,
    )

    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(source,),
        ),
    )

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result=scientific_data,
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    request = AIOrchestrationRequest(
        question="What is the current position of Earth?",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    result = orchestrate_ai_request(request)

    interpretation = (
        result.interpretations.interpretations[0]
    )

    assert interpretation.provenance == (
        source,
    )

def test_orchestrate_uses_language_provider(monkeypatch):
    from astrosphere.ai.llm import (
        AILanguageResponse,
    )

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={
                "status": "success",
            },
        )

    class TestProvider:
        def __init__(self):
            self.request = None

        def generate(self, request):
            self.request = request

            return AILanguageResponse(
                answer="Provider-generated response."
            )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    provider = TestProvider()

    request = AIOrchestrationRequest(
        question="What is Earth's scientific state?",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    result = orchestrate_ai_request(
        request,
        language_provider=provider,
    )

    assert result.answer == (
        "Provider-generated response."
    )

    assert provider.request is not None
    assert provider.request.question == (
        "What is Earth's scientific state?"
    )
    assert provider.request.object.id == "earth"
    assert provider.request.facts.object_id == "earth"
    assert provider.request.interpretations.object_id == (
        "earth"
    )


def test_orchestrate_without_language_provider_preserves_behavior(
    monkeypatch,
):
    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={
                "status": "mocked",
            },
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

    assert result.answer == (
        "AstroSphere retrieved the "
        "scientific-data result for Earth."
    )
