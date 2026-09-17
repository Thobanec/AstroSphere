import pytest

from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretation,
    AIInterpretationSet,
)
from astrosphere.ai.interpreter import (
    interpret_ai_facts,
)


def test_interpreter_renders_scientific_facts():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
                source_capability="scientific-data",
            ),
            AIFact(
                name="position_y",
                value=2.0,
                unit="AU",
                source_capability="scientific-data",
            ),
            AIFact(
                name="position_z",
                value=3.0,
                unit="AU",
                source_capability="scientific-data",
            ),
            AIFact(
                name="velocity_x",
                value=4.0,
                unit="km/s",
                source_capability="scientific-data",
            ),
            AIFact(
                name="velocity_y",
                value=5.0,
                unit="km/s",
                source_capability="scientific-data",
            ),
            AIFact(
                name="velocity_z",
                value=6.0,
                unit="km/s",
                source_capability="scientific-data",
            ),
        ),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert len(result.interpretations) == 6
    assert result.interpretations[0].statement == (
        "Earth position_x is 1.0 AU."
    )
    assert result.interpretations[0].supporting_facts == (
        "position_x",
    )


def test_interpreter_preserves_fact_order():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
            ),
            AIFact(
                name="position_y",
                value=2.0,
                unit="AU",
            ),
            AIFact(
                name="position_z",
                value=3.0,
                unit="AU",
            ),
        ),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert tuple(
        interpretation.supporting_facts[0]
        for interpretation in result.interpretations
    ) == (
        "position_x",
        "position_y",
        "position_z",
    )


def test_interpreter_handles_facts_without_units():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="geomagnetic_kp",
                value=3.0,
                unit=None,
                source_capability="space-weather",
            ),
        ),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert result.interpretations[0].statement == (
        "Earth geomagnetic_kp is 3.0."
    )


def test_interpreter_preserves_observation_context():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
            ),
        ),
        observation_time="2026-09-17T00:00:00Z",
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert result.observation_time == (
        "2026-09-17T00:00:00Z"
    )
    assert result.interpretations[0].observation_time is None


def test_interpreter_preserves_provenance():
    from astrosphere.models.scientific import DataSource

    source = DataSource(
        name="JPL DE440S",
        provider="NASA JPL",
        url="https://ssd.jpl.nasa.gov/planets/eph.html",
    )

    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
            ),
        ),
        provenance=(source,),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert result.provenance == (source,)
    assert result.interpretations[0].provenance == ()


def test_interpreter_preserves_uncertainties():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
            ),
        ),
        uncertainties=(
            "Position is subject to ephemeris uncertainty.",
        ),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert result.uncertainties == (
        "Position is subject to ephemeris uncertainty.",
    )


def test_interpreter_handles_trajectory_facts():
    fact_set = AIFactSet(
        object_id="asteroid:99942",
        facts=(
            AIFact(
                name="orbital_period_days",
                value=323.6,
                unit="days",
                source_capability="trajectory",
            ),
            AIFact(
                name="trajectory_samples",
                value=181,
                unit=None,
                source_capability="trajectory",
            ),
        ),
    )

    result = interpret_ai_facts("Apophis", fact_set)

    assert result.interpretations[0].statement == (
        "Apophis orbital_period_days is 323.6 days."
    )
    assert result.interpretations[1].statement == (
        "Apophis trajectory_samples is 181."
    )


def test_interpreter_handles_close_approach_facts():
    fact_set = AIFactSet(
        object_id="asteroid:99942",
        facts=(
            AIFact(
                name="distance_au",
                value=0.000254,
                unit="AU",
                source_capability="close-approaches",
            ),
            AIFact(
                name="relative_velocity_km_s",
                value=7.42,
                unit="km/s",
                source_capability="close-approaches",
            ),
        ),
    )

    result = interpret_ai_facts("Apophis", fact_set)

    assert result.interpretations[0].statement == (
        "Apophis distance_au is 0.000254 AU."
    )
    assert result.interpretations[1].statement == (
        "Apophis relative_velocity_km_s is 7.42 km/s."
    )


def test_interpreter_handles_orbital_analysis_facts():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="distance_km",
                value=149000000.0,
                unit="km",
                source_capability="orbital-analysis",
            ),
            AIFact(
                name="relative_velocity_km_s",
                value=29.78,
                unit="km/s",
                source_capability="orbital-analysis",
            ),
        ),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert result.interpretations[0].statement == (
        "Earth distance_km is 149000000.0 km."
    )
    assert result.interpretations[1].statement == (
        "Earth relative_velocity_km_s is 29.78 km/s."
    )


def test_interpreter_empty_facts_produces_empty_set():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert result.object_id == "planet:earth"
    assert result.interpretations == ()


def test_interpreter_rejects_invalid_fact_set():
    with pytest.raises(ValueError, match="AIFactSet is required"):
        interpret_ai_facts(
            "Earth",
            None,
        )


def test_interpreter_rejects_empty_subject():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(),
    )

    with pytest.raises(
        ValueError,
        match="Interpretation subject is required",
    ):
        interpret_ai_facts(
            "   ",
            fact_set,
        )


def test_interpreter_does_not_invent_relationships():
    fact_set = AIFactSet(
        object_id="planet:earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
                source_capability="scientific-data",
            ),
        ),
    )

    result = interpret_ai_facts("Earth", fact_set)

    assert len(result.interpretations) == 1
    assert result.interpretations[0].statement == (
        "Earth position_x is 1.0 AU."
    )
