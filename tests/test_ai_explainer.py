import pytest

from astrosphere.ai.explainer import (
    explain_scientific_concept,
)


@pytest.mark.parametrize(
    "subject",
    [
        "position",
        "velocity",
        "trajectory",
        "close_approach",
        "space_weather",
        "solar_wind",
        "magnetic_field",
        "geomagnetic",
        "relationships",
    ],
)
def test_explain_supported_scientific_concept(subject):
    explanation = explain_scientific_concept(subject)

    assert explanation.subject == subject
    assert explanation.explanation
    assert explanation.level == "standard"
    assert explanation.explanation_type == "what"


def test_explain_normalizes_subject_level_and_type():
    explanation = explain_scientific_concept(
        "  VELOCITY  ",
        level="  BEGINNER  ",
        explanation_type="  WHY  ",
    )

    assert explanation.subject == "velocity"
    assert explanation.level == "beginner"
    assert explanation.explanation_type == "why"


@pytest.mark.parametrize(
    "explanation_type",
    [
        "what",
        "why",
        "how",
    ],
)
def test_explain_supports_all_explanation_types(
    explanation_type,
):
    explanation = explain_scientific_concept(
        "velocity",
        explanation_type=explanation_type,
    )

    assert explanation.explanation_type == explanation_type
    assert explanation.explanation


def test_explain_supports_all_levels():
    for level in ("beginner", "standard", "detailed"):
        explanation = explain_scientific_concept(
            "position",
            level=level,
        )

        assert explanation.level == level


@pytest.mark.parametrize(
    "subject",
    [
        "position",
        "velocity",
        "trajectory",
        "close_approach",
        "space_weather",
        "solar_wind",
        "magnetic_field",
        "geomagnetic",
        "relationships",
    ],
)
def test_explanation_depth_changes_by_level(subject):
    beginner = explain_scientific_concept(
        subject,
        level="beginner",
    )
    standard = explain_scientific_concept(
        subject,
        level="standard",
    )
    detailed = explain_scientific_concept(
        subject,
        level="detailed",
    )

    assert beginner.explanation != standard.explanation
    assert standard.explanation != detailed.explanation
    assert beginner.explanation != detailed.explanation


@pytest.mark.parametrize(
    "explanation_type",
    [
        "what",
        "why",
        "how",
    ],
)
def test_explanation_type_changes_content(explanation_type):
    what = explain_scientific_concept(
        "velocity",
        explanation_type="what",
    )
    requested = explain_scientific_concept(
        "velocity",
        explanation_type=explanation_type,
    )

    if explanation_type == "what":
        assert requested.explanation == what.explanation
    else:
        assert requested.explanation != what.explanation


def test_why_velocity_explains_direction():
    explanation = explain_scientific_concept(
        "velocity",
        explanation_type="why",
        level="standard",
    )

    assert "direction" in explanation.explanation


def test_how_velocity_explains_rate_of_change():
    explanation = explain_scientific_concept(
        "velocity",
        explanation_type="how",
        level="standard",
    )

    assert "rate of change" in explanation.explanation


def test_how_close_approach_explains_minimum_separation():
    explanation = explain_scientific_concept(
        "close_approach",
        explanation_type="how",
        level="standard",
    )

    assert "minimum" in explanation.explanation
    assert "separation" in explanation.explanation


def test_explain_rejects_unknown_concept():
    with pytest.raises(
        ValueError,
        match="Unsupported scientific concept",
    ):
        explain_scientific_concept("black_hole")


def test_explain_rejects_unknown_level():
    with pytest.raises(
        ValueError,
        match="Unsupported explanation level",
    ):
        explain_scientific_concept(
            "velocity",
            level="expert",
        )


def test_explain_rejects_unknown_explanation_type():
    with pytest.raises(
        ValueError,
        match="Unsupported explanation type",
    ):
        explain_scientific_concept(
            "velocity",
            explanation_type="when",
        )


def test_explain_rejects_empty_subject():
    with pytest.raises(
        ValueError,
        match="Explanation subject is required",
    ):
        explain_scientific_concept("")


def test_explain_rejects_empty_level():
    with pytest.raises(
        ValueError,
        match="Explanation level is required",
    ):
        explain_scientific_concept(
            "velocity",
            level="",
        )


def test_explain_rejects_empty_explanation_type():
    with pytest.raises(
        ValueError,
        match="Explanation type is required",
    ):
        explain_scientific_concept(
            "velocity",
            explanation_type="",
        )
