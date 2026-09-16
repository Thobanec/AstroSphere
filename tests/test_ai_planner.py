from astrosphere.ai import (
    AICapabilityPlanItem,
    AIOrchestrationRequest,
    plan_ai_capabilities,
)


def test_plan_single_capability():
    request = AIOrchestrationRequest(
        question="What is Earth's scientific state?",
        object_id="earth",
        capability_ids=("scientific-data",),
    )

    plan = plan_ai_capabilities(request)

    assert len(plan) == 1
    assert isinstance(
        plan[0],
        AICapabilityPlanItem,
    )
    assert plan[0].capability_id == "scientific-data"
    assert plan[0].execution_order == 1
    assert "Earth's scientific state" in plan[0].reason


def test_plan_multiple_capabilities_preserves_order():
    request = AIOrchestrationRequest(
        question="Analyze Apophis.",
        object_id="asteroid:99942",
        capability_ids=(
            "scientific-data",
            "tracking",
            "close-approaches",
        ),
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == [
        "scientific-data",
        "tracking",
        "close-approaches",
    ]

    assert [
        item.execution_order
        for item in plan
    ] == [1, 2, 3]


def test_plan_normalizes_capability_ids():
    request = AIOrchestrationRequest(
        question="Check space weather.",
        object_id="earth",
        capability_ids=(
            " SPACE-WEATHER ",
        ),
    )

    plan = plan_ai_capabilities(request)

    assert plan[0].capability_id == "space-weather"


def test_plan_rejects_unavailable_capability():
    request = AIOrchestrationRequest(
        question="Show Earth's trajectory.",
        object_id="earth",
        capability_ids=("trajectory",),
    )

    try:
        plan_ai_capabilities(request)
    except ValueError as exc:
        assert "not available" in str(exc)
    else:
        raise AssertionError(
            "Expected unavailable capability to be rejected."
        )


def test_plan_rejects_invalid_request():
    try:
        plan_ai_capabilities(object())
    except ValueError as exc:
        assert "AIOrchestrationRequest is required" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid request to be rejected."
        )


def test_plan_uses_all_available_capabilities_when_unspecified():
    request = AIOrchestrationRequest(
        question="Inspect the Sun.",
        object_id="sun",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == [
        "context",
        "relationships",
    ]


def test_plan_preserves_request_parameters():
    parameters = {
        "samples": 10,
    }

    request = AIOrchestrationRequest(
        question="Show the Apophis trajectory.",
        object_id="asteroid:99942",
        capability_ids=("trajectory",),
        parameters=parameters,
    )

    plan = plan_ai_capabilities(request)

    assert plan[0].parameters == parameters


def test_plan_returns_immutable_tuple():
    request = AIOrchestrationRequest(
        question="Inspect Earth.",
        object_id="earth",
        capability_ids=("context",),
    )

    plan = plan_ai_capabilities(request)

    assert isinstance(plan, tuple)
