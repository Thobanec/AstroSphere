from astrosphere.ai.intent import (
    AICapabilityIntent,
)
from astrosphere.ai.question_understanding import (
    understand_scientific_question,
)


def test_understands_position_question():
    result = understand_scientific_question(
        "Where is Apophis?",
        object_id="asteroid:99942",
    )

    assert result.question == "Where is Apophis?"
    assert result.object_id == "asteroid:99942"
    assert result.requested_information == (
        "position",
    )
    assert result.temporal_context == "current"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["tracking"]


def test_understands_velocity_question():
    result = understand_scientific_question(
        "How fast is Apophis moving?",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "velocity",
    )
    assert result.temporal_context == "current"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["scientific-data"]


def test_understands_trajectory_question():
    result = understand_scientific_question(
        "Show me the trajectory of Apophis.",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "trajectory",
    )
    assert result.temporal_context == "future"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["trajectory"]


def test_understands_close_approach_question():
    result = understand_scientific_question(
        "When is Apophis's closest approach to Earth?",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "close_approach",
    )
    assert result.temporal_context == "future"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["close-approaches"]


def test_understands_how_close_apophis_gets_to_earth():
    result = understand_scientific_question(
        "How close does Apophis get to Earth?",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "close_approach",
    )
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["close-approaches"]

def test_understands_space_weather_question():
    result = understand_scientific_question(
        "What is the current solar wind speed?",
        object_id="earth",
    )

    assert result.requested_information == (
        "space_weather",
    )
    assert result.temporal_context == "current"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["space-weather"]


def test_understands_relationship_question():
    result = understand_scientific_question(
        "Show Earth's hierarchy and ancestors.",
        object_id="earth",
    )

    assert result.requested_information == (
        "relationships",
    )
    assert result.temporal_context == "unspecified"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["relationships"]


def test_understands_context_question():
    result = understand_scientific_question(
        "Tell me about Earth.",
        object_id="earth",
    )

    assert result.requested_information == (
        "context",
    )
    assert result.temporal_context == "unspecified"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == ["context"]


def test_understanding_preserves_multiple_intents():
    result = understand_scientific_question(
        "Show Apophis's current position and trajectory.",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "position",
        "trajectory",
    )
    assert [
        intent.capability_id
        for intent in result.intents
    ] == [
        "tracking",
        "trajectory",
    ]


def test_unknown_question_has_no_requested_information():
    result = understand_scientific_question(
        "Hello AstroSphere.",
        object_id="earth",
    )

    assert result.requested_information == ()
    assert result.temporal_context == "unspecified"
    assert result.intents == ()


def test_question_is_required():
    try:
        understand_scientific_question(
            "",
            object_id="earth",
        )
    except ValueError as exc:
        assert str(exc) == "AI question is required."
    else:
        raise AssertionError(
            "Expected question validation error."
        )


def test_object_id_is_optional():
    result = understand_scientific_question(
        "Where is Apophis?"
    )

    assert result.object_id is None

def test_understanding_position_and_close_approach():
    result = understand_scientific_question(
        "Where is Apophis and when is its closest approach to Earth?",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "position",
        "close_approach",
    )
    assert result.temporal_context == "current"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == [
        "tracking",
        "close-approaches",
    ]


def test_understanding_position_and_trajectory():
    result = understand_scientific_question(
        "Where is Apophis and what is its trajectory?",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "position",
        "trajectory",
    )
    assert result.temporal_context == "current"
    assert result.temporal_contexts == (
        ("position", "current"),
        ("trajectory", "future"),
    )
    assert [
        intent.capability_id
        for intent in result.intents
    ] == [
        "tracking",
        "trajectory",
    ]


def test_understanding_trajectory_and_close_approach():
    result = understand_scientific_question(
        "What is Apophis's trajectory and when is its closest approach to Earth?",
        object_id="asteroid:99942",
    )

    assert result.requested_information == (
        "trajectory",
        "close_approach",
    )
    assert result.temporal_context == "future"
    assert [
        intent.capability_id
        for intent in result.intents
    ] == [
        "trajectory",
        "close-approaches",
    ]


def test_understanding_earth_position_and_space_weather():
    result = understand_scientific_question(
        "What is Earth's position and the current solar wind speed?",
        object_id="earth",
    )

    assert result.requested_information == (
        "position",
        "space_weather",
    )
    assert result.temporal_context == "current"

