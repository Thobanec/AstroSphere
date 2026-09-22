import pytest

from astrosphere.ai.explanation import (
    AIExplanationSet,
)
from astrosphere.ai.explanation_builder import (
    build_fact_grounded_explanation,
)
from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretation,
    AIInterpretationSet,
)


def test_builds_position_explanation_from_facts():
    fact_set = AIFactSet(
        object_id="earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="km",
                source_capability="scientific-data",
            ),
            AIFact(
                name="position_y",
                value=2.0,
                unit="km",
                source_capability="scientific-data",
            ),
        ),
    )

    interpretation_set = AIInterpretationSet(
        object_id="earth",
        interpretations=(
            AIInterpretation(
                subject="position_x",
                statement="Position fact position_x is 1.0 km.",
                supporting_facts=("position_x",),
                supporting_capabilities=("scientific-data",),
            ),
        ),
    )

    result = build_fact_grounded_explanation(
        "earth",
        fact_set,
        interpretation_set,
        "position",
    )

    assert isinstance(result, AIExplanationSet)
    assert result.object_id == "earth"
    assert len(result.explanations) == 1

    explanation = result.explanations[0]

    assert explanation.subject == "position"
    assert explanation.supporting_facts == (
        "position_x",
        "position_y",
    )
    assert explanation.supporting_interpretations == (
        "Position fact position_x is 1.0 km.",
    )


def test_builds_velocity_explanation_from_velocity_facts():
    fact_set = AIFactSet(
        object_id="asteroid:99942",
        facts=(
            AIFact(
                name="velocity_x",
                value=1.2,
                unit="km/s",
                source_capability="scientific-data",
            ),
            AIFact(
                name="velocity_y",
                value=3.4,
                unit="km/s",
                source_capability="scientific-data",
            ),
        ),
    )

    result = build_fact_grounded_explanation(
        "asteroid:99942",
        fact_set,
        AIInterpretationSet(
            object_id="asteroid:99942",
        ),
        "velocity",
        level="detailed",
    )

    assert result.level == "detailed"
    assert result.explanations[0].supporting_facts == (
        "velocity_x",
        "velocity_y",
    )


def test_preserves_provenance_and_uncertainties():
    fact_set = AIFactSet(
        object_id="earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="km",
            ),
        ),
        observation_time="2026-09-18T00:00:00Z",
        uncertainties=("Fact uncertainty",),
    )

    interpretation_set = AIInterpretationSet(
        object_id="earth",
        interpretations=(
            AIInterpretation(
                subject="position_x",
                statement="Position fact position_x is 1.0 km.",
            ),
        ),
        uncertainties=("Interpretation uncertainty",),
    )

    result = build_fact_grounded_explanation(
        "earth",
        fact_set,
        interpretation_set,
        "position",
    )

    explanation = result.explanations[0]

    assert explanation.observation_time == (
        "2026-09-18T00:00:00Z"
    )
    assert explanation.uncertainties == (
        "Fact uncertainty",
        "Interpretation uncertainty",
    )


def test_rejects_missing_supporting_facts():
    fact_set = AIFactSet(
        object_id="earth",
        facts=(
            AIFact(
                name="velocity_x",
                value=1.0,
                unit="km/s",
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="No supporting facts available",
    ):
        build_fact_grounded_explanation(
            "earth",
            fact_set,
            AIInterpretationSet(
                object_id="earth",
            ),
            "position",
        )


def test_rejects_invalid_fact_set():
    with pytest.raises(
        ValueError,
        match="AIFactSet is required",
    ):
        build_fact_grounded_explanation(
            "earth",
            None,
            AIInterpretationSet(
                object_id="earth",
            ),
            "position",
        )
