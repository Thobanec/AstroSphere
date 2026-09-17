import pytest

from astrosphere.ai.interpretation import (
    AIInterpretation,
    AIInterpretationSet,
)
from astrosphere.models.scientific import (
    DataSource,
)


def test_ai_interpretation_defaults():
    interpretation = AIInterpretation(
        subject="Earth",
        statement="Earth has a measured position.",
    )

    assert interpretation.subject == "Earth"
    assert interpretation.statement == (
        "Earth has a measured position."
    )
    assert interpretation.supporting_facts == ()
    assert interpretation.observation_time is None
    assert interpretation.provenance == ()
    assert interpretation.uncertainties == ()


def test_ai_interpretation_preserves_supporting_facts():
    interpretation = AIInterpretation(
        subject="Earth",
        statement="Earth has a measured position.",
        supporting_facts=(
            "position_x",
            "position_y",
            "position_z",
        ),
    )

    assert interpretation.supporting_facts == (
        "position_x",
        "position_y",
        "position_z",
    )


def test_ai_interpretation_preserves_provenance():
    source = DataSource(
        name="Test Source",
        provider="Test Provider",
    )

    interpretation = AIInterpretation(
        subject="Earth",
        statement="Earth has a measured position.",
        provenance=(source,),
    )

    assert interpretation.provenance == (source,)


def test_ai_interpretation_set_defaults():
    interpretation_set = AIInterpretationSet(
        object_id="earth",
    )

    assert interpretation_set.object_id == "earth"
    assert interpretation_set.interpretations == ()
    assert interpretation_set.observation_time is None
    assert interpretation_set.provenance == ()
    assert interpretation_set.uncertainties == ()


def test_ai_interpretation_set_preserves_interpretations():
    interpretation = AIInterpretation(
        subject="Earth",
        statement="Earth has a measured position.",
        supporting_facts=("position_x",),
    )

    interpretation_set = AIInterpretationSet(
        object_id="earth",
        interpretations=(interpretation,),
    )

    assert interpretation_set.interpretations == (
        interpretation,
    )


def test_ai_interpretation_models_are_immutable():
    interpretation = AIInterpretation(
        subject="Earth",
        statement="Earth has a measured position.",
    )

    with pytest.raises(AttributeError):
        interpretation.subject = "Mars"

    interpretation_set = AIInterpretationSet(
        object_id="earth",
    )

    with pytest.raises(AttributeError):
        interpretation_set.object_id = "mars"
