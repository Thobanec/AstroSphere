from astrosphere.ai.intent import (
    AICapabilityIntent,
)
from astrosphere.ai.scientific_question import (
    AIScientificQuestion,
)


def test_scientific_question_defaults():
    question = AIScientificQuestion(
        question="Where is Apophis?"
    )

    assert question.question == "Where is Apophis?"
    assert question.object_id is None
    assert question.requested_information == ()
    assert question.temporal_context is None
    assert question.intents == ()


def test_scientific_question_stores_structured_information():
    intent = AICapabilityIntent(
        capability_id="tracking",
        reason="Question matched the 'where is' intent.",
    )

    question = AIScientificQuestion(
        question="Where is Apophis?",
        object_id="asteroid:99942",
        requested_information=("position",),
        temporal_context="current",
        intents=(intent,),
    )

    assert question.object_id == "asteroid:99942"
    assert question.requested_information == (
        "position",
    )
    assert question.temporal_context == "current"
    assert question.intents == (intent,)


def test_scientific_question_is_immutable():
    question = AIScientificQuestion(
        question="Where is Earth?"
    )

    try:
        question.question = "Changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "Expected AIScientificQuestion to be immutable."
        )
