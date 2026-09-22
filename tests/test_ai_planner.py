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
    assert plan[0].reason == (
        "Question matched the 'scientific state' intent."
    )


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
        "scientific-data",
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

def test_plan_question_selects_tracking():
    request = AIOrchestrationRequest(
        question="Where is Apophis?",
        object_id="asteroid:99942",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["tracking"]

    assert plan[0].reason == (
        "Question matched the 'where is' intent."
    )


def test_plan_question_selects_trajectory():
    request = AIOrchestrationRequest(
        question="Show me the trajectory of Apophis.",
        object_id="asteroid:99942",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["trajectory"]


def test_plan_question_selects_close_approaches():
    request = AIOrchestrationRequest(
        question="When is Apophis's closest approach to Earth?",
        object_id="asteroid:99942",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["close-approaches"]


def test_plan_question_selects_space_weather():
    request = AIOrchestrationRequest(
        question="What is the current solar wind speed?",
        object_id="earth",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["space-weather"]


def test_plan_question_selects_scientific_data():
    request = AIOrchestrationRequest(
        question="Show me the position and velocity.",
        object_id="earth",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["scientific-data"]


def test_plan_question_selects_context_for_generic_question():
    request = AIOrchestrationRequest(
        question="Tell me about Earth.",
        object_id="earth",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["context"]


def test_plan_question_selects_planetary_trajectory():
    request = AIOrchestrationRequest(
        question="Show the trajectory of Earth.",
        object_id="earth",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == ["planetary-trajectory"]

def test_plan_compound_position_and_trajectory_question():
    request = AIOrchestrationRequest(
        question="Where is Apophis and what is its trajectory?",
        object_id="asteroid:99942",
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == [
        "tracking",
        "trajectory",
    ]

    assert [
        item.execution_order
        for item in plan
    ] == [1, 2]

def test_plan_compound_parameters_are_routed_per_capability():
    request = AIOrchestrationRequest(
        question="Where is Earth and what is its trajectory?",
        object_id="earth",
        parameters={
            "days": 5,
            "samples": 5,
        },
    )

    plan = plan_ai_capabilities(request)

    assert [
        item.capability_id
        for item in plan
    ] == [
        "scientific-data",
        "planetary-trajectory",
    ]

    assert plan[0].parameters == {}

    assert plan[1].parameters == {
        "days": 5,
        "samples": 5,
    }
