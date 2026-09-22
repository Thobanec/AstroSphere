from astrosphere.ai.explanation import (
    AIExplanation,
    AIExplanationSet,
)


def test_ai_explanation_defaults():
    explanation = AIExplanation(
        subject="velocity",
        explanation="Velocity describes how an object changes position over time.",
    )

    assert explanation.subject == "velocity"
    assert explanation.explanation.startswith("Velocity")
    assert explanation.level == "standard"
    assert explanation.supporting_facts == ()
    assert explanation.supporting_interpretations == ()
    assert explanation.provenance == ()
    assert explanation.uncertainties == ()


def test_ai_explanation_preserves_grounding_metadata():
    explanation = AIExplanation(
        subject="position",
        explanation="Position describes where the object is relative to the selected reference frame.",
        level="detailed",
        supporting_facts=("position_x", "position_y", "position_z"),
        supporting_interpretations=("Position fact position_x is ...",),
        observation_time="2026-09-18T00:00:00Z",
        uncertainties=("Position depends on the supplied observation time.",),
    )

    assert explanation.level == "detailed"
    assert explanation.supporting_facts == (
        "position_x",
        "position_y",
        "position_z",
    )
    assert explanation.supporting_interpretations == (
        "Position fact position_x is ...",
    )
    assert explanation.observation_time == "2026-09-18T00:00:00Z"
    assert explanation.uncertainties == (
        "Position depends on the supplied observation time.",
    )


def test_ai_explanation_set_defaults():
    explanation_set = AIExplanationSet(
        object_id="earth",
    )

    assert explanation_set.object_id == "earth"
    assert explanation_set.explanations == ()
    assert explanation_set.level == "standard"
    assert explanation_set.provenance == ()
    assert explanation_set.uncertainties == ()


def test_ai_explanation_set_preserves_explanations():
    explanation = AIExplanation(
        subject="velocity",
        explanation="Velocity describes change in position over time.",
        level="beginner",
    )

    explanation_set = AIExplanationSet(
        object_id="earth",
        explanations=(explanation,),
        level="beginner",
    )

    assert explanation_set.explanations == (explanation,)
    assert explanation_set.level == "beginner"


def test_ai_explanation_models_are_immutable():
    explanation = AIExplanation(
        subject="velocity",
        explanation="Velocity describes change in position over time.",
    )

    try:
        explanation.subject = "position"
        assert False
    except AttributeError:
        pass
