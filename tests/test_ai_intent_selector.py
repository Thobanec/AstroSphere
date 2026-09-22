from astrosphere.ai.intent import (
    AICapabilityIntent,
)
from astrosphere.ai.intent_selector import (
    select_capability_intents,
)


def test_select_tracking_intent():
    intents = select_capability_intents(
        "Where is Apophis?"
    )

    assert intents == (
        AICapabilityIntent(
            capability_id="tracking",
            reason="Question matched the 'where is' intent.",
        ),
    )


def test_select_trajectory_intent():
    intents = select_capability_intents(
        "Show me the trajectory of Apophis."
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["trajectory"]


def test_select_close_approach_intent():
    intents = select_capability_intents(
        "When is Apophis's closest approach to Earth?"
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["close-approaches"]


def test_select_space_weather_intent():
    intents = select_capability_intents(
        "What is the current solar wind speed?"
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["space-weather"]


def test_select_scientific_data_intent():
    intents = select_capability_intents(
        "Show me the position and velocity."
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["scientific-data"]


def test_select_relationship_intent():
    intents = select_capability_intents(
        "Show the hierarchy and ancestors."
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["relationships"]


def test_select_context_intent():
    intents = select_capability_intents(
        "Tell me about Earth."
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["context"]


def test_select_multiple_intents():
    intents = select_capability_intents(
        "Show Apophis's current position and trajectory."
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == [
        "tracking",
        "trajectory",
    ]


def test_no_matching_intent_returns_empty_tuple():
    intents = select_capability_intents(
        "Hello AstroSphere."
    )

    assert intents == ()


def test_empty_question_rejected():
    try:
        select_capability_intents("")
    except ValueError as exc:
        assert "AI question is required" in str(exc)
    else:
        raise AssertionError(
            "Expected empty question to be rejected."
        )


def test_non_string_question_rejected():
    try:
        select_capability_intents(None)
    except ValueError as exc:
        assert "AI question is required" in str(exc)
    else:
        raise AssertionError(
            "Expected non-string question to be rejected."
        )

def test_specific_intent_takes_precedence_over_context():
    intents = select_capability_intents(
        "What is the current position of Apophis?"
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["tracking"]

def test_position_falls_back_to_scientific_data_when_tracking_unavailable():
    intents = select_capability_intents(
        "What is the current position of Earth?",
        available_capabilities={
            "context",
            "scientific-data",
            "relationships",
            "space-weather",
            "orbital-analysis",
        },
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["scientific-data"]


def test_position_keeps_tracking_when_tracking_available():
    intents = select_capability_intents(
        "What is the current position of Apophis?",
        available_capabilities={
            "context",
            "scientific-data",
            "relationships",
            "tracking",
            "trajectory",
            "close-approaches",
        },
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["tracking"]

def test_trajectory_falls_back_to_orbital_analysis_when_trajectory_unavailable():
    intents = select_capability_intents(
        "What is Earth's orbital trajectory?",
        available_capabilities={
            "context",
            "scientific-data",
            "relationships",
            "space-weather",
            "orbital-analysis",
        },
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["orbital-analysis"]


def test_trajectory_maps_to_planetary_trajectory_when_available():
    intents = select_capability_intents(
        "What is Earth's orbital trajectory?",
        available_capabilities={
            "context",
            "scientific-data",
            "relationships",
            "space-weather",
            "orbital-analysis",
            "planetary-trajectory",
        },
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["planetary-trajectory"]


def test_asteroid_trajectory_remains_trajectory_capability():
    intents = select_capability_intents(
        "What is Apophis's trajectory?",
        available_capabilities={
            "context",
            "scientific-data",
            "relationships",
            "tracking",
            "trajectory",
            "close-approaches",
            "space-weather",
            "orbital-analysis",
            "planetary-trajectory",
        },
    )

    assert [
        intent.capability_id
        for intent in intents
    ] == ["trajectory"]
