from astrosphere.ai import (
    AIResponse,
    build_ai_context,
    compose_ai_response,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def test_compose_single_capability_response():
    context = build_ai_context(
        "What is the current position of Apophis?",
        "asteroid:99942",
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "designation": "99942",
            "status": "success",
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert isinstance(response, AIResponse)
    assert response.question == (
        "What is the current position of Apophis?"
    )
    assert response.object_id == "asteroid:99942"
    assert "tracking" in response.answer
    assert "Apophis" in response.answer
    assert response.results == (result,)


def test_compose_multiple_capability_results():
    context = build_ai_context(
        "Show the position and trajectory of Apophis.",
        "asteroid:99942",
    )

    tracking_result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "status": "success",
        },
    )

    trajectory_result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="trajectory",
        result={
            "status": "success",
            "samples": 181,
        },
    )

    response = compose_ai_response(
        context,
        (
            tracking_result,
            trajectory_result,
        ),
    )

    assert response.results == (
        tracking_result,
        trajectory_result,
    )
    assert response.results[0].capability_id == "tracking"
    assert response.results[1].capability_id == "trajectory"
    assert "tracking" in response.answer
    assert "trajectory" in response.answer


def test_compose_preserves_grounded_provenance():
    context = build_ai_context(
        "What scientific data is available for Earth?",
        "earth",
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result={
            "status": "success",
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    source_names = tuple(
        source.name
        for source in response.provenance
    )

    assert "JPL DE440S" in source_names
    assert "JPL Planetary Physical Parameters" in source_names


def test_compose_collects_result_provenance():
    context = build_ai_context(
        "What is the current position of Apophis?",
        "asteroid:99942",
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "status": "success",
            "provenance": context.provenance,
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.provenance == context.provenance


def test_compose_rejects_invalid_results():
    context = build_ai_context(
        "What is Apophis?",
        "asteroid:99942",
    )

    try:
        compose_ai_response(
            context,
            ("invalid-result",),
        )
    except ValueError as exc:
        assert "CapabilityExecutionResult" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid capability result to be rejected."
        )


def test_compose_empty_results():
    context = build_ai_context(
        "What is Apophis?",
        "asteroid:99942",
    )

    response = compose_ai_response(
        context,
        (),
    )

    assert isinstance(response, AIResponse)
    assert response.results == ()
    assert "No capability results" in response.answer
