from datetime import datetime, timezone

import pytest

from astrosphere.ai.fact_extractor import (
    extract_ai_facts,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)
from astrosphere.models.scientific import (
    DataSource,
    Geomagnetic,
    MagneticField,
    Observation,
    Position,
    ScientificData,
    ScientificProvenance,
    SolarWind,
    SpaceWeatherData,
    Velocity,
)


def test_extract_scientific_position_and_velocity():
    source = DataSource(
        name="Test Source",
        provider="Test Provider",
    )

    scientific_data = ScientificData(
        object_id="earth",
        observation=Observation(
            observation_time="2026-09-16T10:00:00+00:00",
            source=source,
        ),
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=4.0,
            y=5.0,
            z=6.0,
            unit="AU/day",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(source,),
            reference_frames=("ICRF",),
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    assert fact_set.object_id == "earth"
    assert fact_set.observation_time == (
        "2026-09-16T10:00:00+00:00"
    )

    names = [fact.name for fact in fact_set.facts]

    assert names == [
        "position_x",
        "position_y",
        "position_z",
        "velocity_x",
        "velocity_y",
        "velocity_z",
    ]

    assert fact_set.facts[0].value == 1.0
    assert fact_set.facts[0].unit == "AU"
    assert fact_set.facts[0].metadata["frame"] == "ICRF"

    assert fact_set.facts[3].value == 4.0
    assert fact_set.facts[3].unit == "AU/day"

    assert fact_set.provenance == (source,)


def test_extract_space_weather_facts():
    source = DataSource(
        name="NOAA SWPC",
        provider="NOAA",
    )

    weather = SpaceWeatherData(
        observation_time="2026-09-16T10:00:00+00:00",
        solar_wind=SolarWind(
            speed_km_s=450.0,
            density_cm3=5.0,
            temperature_k=100000.0,
        ),
        magnetic_field=MagneticField(
            bt_nt=6.0,
            bz_nt=-2.5,
        ),
        geomagnetic=Geomagnetic(
            kp=3.0,
        ),
        provenance=ScientificProvenance(
            sources=(source,),
            reference_frames=("GSM",),
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="space-weather",
        result=weather,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    names = [fact.name for fact in fact_set.facts]

    assert names == [
        "solar_wind_speed",
        "solar_wind_density",
        "solar_wind_temperature",
        "magnetic_field_bt",
        "magnetic_field_bz_gsm",
        "geomagnetic_kp",
    ]

    assert fact_set.facts[0].value == 450.0
    assert fact_set.facts[0].unit == "km/s"

    bz = fact_set.facts[4]
    assert bz.value == -2.5
    assert bz.unit == "nT"
    assert bz.metadata["frame"] == "GSM"

    assert fact_set.provenance == (source,)


def test_extract_trajectory_facts():
    trajectory = {
        "observation_time": (
            "2026-09-16T10:00:00+00:00"
        ),
        "orbital_period_days": 323.6,
        "samples": 181,
        "coordinate_frame": (
            "heliocentric_ecliptic"
        ),
        "points": [
            {
                "observation_time": (
                    "2026-09-16T10:00:00+00:00"
                ),
                "x": 1.0,
                "y": 2.0,
                "z": 3.0,
            }
        ],
    }

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="trajectory",
        result=trajectory,
    )

    fact_set = extract_ai_facts(
        "asteroid:99942",
        (result,),
    )

    names = [fact.name for fact in fact_set.facts]

    assert names == [
        "trajectory_observation_time",
        "orbital_period",
        "trajectory_sample_count",
        "trajectory_coordinate_frame",
    ]

    assert fact_set.facts[1].value == 323.6
    assert fact_set.facts[1].unit == "days"
    assert fact_set.facts[2].value == 181


def test_extract_cross_capability_earth_facts():
    scientific_source = DataSource(
        name="JPL DE440S",
        provider="NASA/JPL",
        dataset="DE440S",
    )

    scientific_data = ScientificData(
        object_id="earth",
        observation=Observation(
            observation_time="2026-09-21T12:00:00+00:00",
            source=scientific_source,
        ),
        position=Position(
            x=1.002,
            y=-0.032,
            z=-0.014,
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=0.0002,
            y=0.0157,
            z=0.0068,
            unit="AU/day",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(scientific_source,),
            reference_frames=("ICRF",),
        ),
    )

    scientific_result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    trajectory_result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="planetary-trajectory",
        result=[
            {
                "date": "2026-09-21T12:00:00+00:00",
                "x_au": 1.003,
                "y_au": -0.023,
                "z_au": 0.0,
            },
            {
                "date": "2026-09-26T12:00:00+00:00",
                "x_au": 1.001,
                "y_au": 0.063,
                "z_au": 0.0,
            },
        ],
    )

    fact_set = extract_ai_facts(
        "earth",
        (
            scientific_result,
            trajectory_result,
        ),
    )

    assert fact_set.object_id == "earth"

    scientific_facts = [
        fact
        for fact in fact_set.facts
        if fact.source_capability == "scientific-data"
    ]

    trajectory_facts = [
        fact
        for fact in fact_set.facts
        if fact.source_capability == "planetary-trajectory"
    ]

    assert scientific_facts
    assert trajectory_facts

    scientific_names = {
        fact.name
        for fact in scientific_facts
    }

    trajectory_names = {
        fact.name
        for fact in trajectory_facts
    }

    assert {
        "position_x",
        "position_y",
        "position_z",
        "velocity_x",
        "velocity_y",
        "velocity_z",
    }.issubset(scientific_names)

    assert {
        "trajectory_sample_count",
        "trajectory_start_date",
        "trajectory_end_date",
        "trajectory_coordinate_frame",
        "trajectory_start_x",
        "trajectory_end_x",
        "trajectory_start_y",
        "trajectory_end_y",
        "trajectory_start_z",
        "trajectory_end_z",
    }.issubset(trajectory_names)

    position_x = next(
        fact
        for fact in scientific_facts
        if fact.name == "position_x"
    )

    assert position_x.value == 1.002
    assert position_x.unit == "AU"
    assert position_x.metadata["frame"] == "ICRF"

    sample_count = next(
        fact
        for fact in trajectory_facts
        if fact.name == "trajectory_sample_count"
    )

    assert sample_count.value == 2

    assert scientific_source in fact_set.provenance


def test_cross_capability_facts_preserve_evidence_traceability():
    scientific_source = DataSource(
        name="JPL DE440S",
        provider="NASA/JPL",
        dataset="DE440S",
    )

    scientific_data = ScientificData(
        object_id="earth",
        observation=Observation(
            observation_time="2026-09-21T12:00:00+00:00",
            source=scientific_source,
        ),
        position=Position(
            x=1.002,
            y=-0.032,
            z=-0.014,
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=0.0002,
            y=0.0157,
            z=0.0068,
            unit="AU/day",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(scientific_source,),
            reference_frames=("ICRF",),
        ),
    )

    scientific_result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    trajectory_result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="planetary-trajectory",
        result=[
            {
                "date": "2026-09-21T12:00:00+00:00",
                "x_au": 1.003,
                "y_au": -0.023,
                "z_au": 0.0,
            },
            {
                "date": "2026-09-26T12:00:00+00:00",
                "x_au": 1.001,
                "y_au": 0.063,
                "z_au": 0.0,
            },
        ],
    )

    fact_set = extract_ai_facts(
        "earth",
        (
            scientific_result,
            trajectory_result,
        ),
    )

    scientific_facts = tuple(
        fact
        for fact in fact_set.facts
        if fact.source_capability == "scientific-data"
    )

    trajectory_facts = tuple(
        fact
        for fact in fact_set.facts
        if fact.source_capability == "planetary-trajectory"
    )

    assert scientific_facts
    assert trajectory_facts

    assert all(
        fact.source_capability == "scientific-data"
        for fact in scientific_facts
    )

    assert all(
        fact.source_capability == "planetary-trajectory"
        for fact in trajectory_facts
    )

    assert scientific_source in fact_set.provenance

    assert all(
        fact.metadata.get("frame") == "ICRF"
        for fact in scientific_facts
        if fact.name.startswith("position_")
        or fact.name.startswith("velocity_")
    )


def test_extract_orbital_analysis_facts():
    analysis = [
        {
            "date": datetime(
                2026,
                9,
                16,
            ),
            "distance_km": 150000000.0,
            "relative_velocity_km_s": 29.5,
        },
    ]

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="orbital-analysis",
        result=analysis,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    names = [fact.name for fact in fact_set.facts]

    assert names == [
        "analysis_date",
        "body_distance",
        "relative_velocity",
    ]

    assert fact_set.facts[1].value == 150000000.0
    assert fact_set.facts[1].unit == "km"

    assert fact_set.facts[2].value == 29.5
    assert fact_set.facts[2].unit == "km/s"


def test_unknown_capability_produces_no_facts():
    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="unknown-capability",
        result={
            "secret_value": 123,
        },
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    assert fact_set.facts == ()
    assert fact_set.provenance == ()


def test_invalid_result_is_rejected():
    with pytest.raises(ValueError):
        extract_ai_facts(
            "earth",
            ("not-a-capability-result",),
        )


def test_empty_object_id_is_rejected():
    with pytest.raises(ValueError):
        extract_ai_facts(
            " ",
            (),
        )


def test_multiple_results_preserve_order_and_merge_provenance():
    source = DataSource(
        name="Test Source",
        provider="Test",
    )

    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(source,),
        ),
    )

    scientific_result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    weather = SpaceWeatherData(
        observation_time="2026-09-16T10:00:00+00:00",
        solar_wind=SolarWind(
            speed_km_s=400.0,
        ),
        provenance=ScientificProvenance(
            sources=(source,),
        ),
    )

    weather_result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="space-weather",
        result=weather,
    )

    fact_set = extract_ai_facts(
        "EARTH",
        (
            scientific_result,
            weather_result,
        ),
    )

    assert fact_set.object_id == "earth"

    assert fact_set.facts[0].name == "position_x"
    assert fact_set.facts[3].name == "solar_wind_speed"

    assert fact_set.provenance == (source,)


def test_missing_scientific_components_do_not_create_facts():
    scientific_data = ScientificData(
        object_id="earth",
        position=None,
        velocity=None,
        provenance=None,
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    assert fact_set.facts == ()
    assert fact_set.observation_time is None
    assert fact_set.provenance == ()
from astrosphere.ai.fact_extractor import (
    extract_ai_facts,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)
from astrosphere.models.close_approach import (
    CloseApproach,
)
from astrosphere.models.scientific import (
    DataSource,
)


def test_extract_close_approach_facts():
    source = DataSource(
        name="NASA/JPL SBDB Close Approach Data API",
        provider="NASA/JPL CNEOS",
    )

    approach = CloseApproach(
        object_id="asteroid:99942",
        designation="99942",
        fullname="99942 Apophis (2004 MN4)",
        close_approach_time="2029-Apr-13 21:46",
        distance_au=0.000254090910419299,
        distance_min_au=0.000254068999976389,
        distance_max_au=0.000254112821017663,
        distance_km=38000.0,
        distance_min_km=37996.0,
        distance_max_km=38003.0,
        relative_velocity_km_s=7.42253895678452,
        orbit_id="123",
        source=source,
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="close-approaches",
        result=(approach,),
    )

    fact_set = extract_ai_facts(
        "asteroid:99942",
        (result,),
    )

    names = [
        fact.name
        for fact in fact_set.facts
    ]

    assert names == [
        "close_approach_time",
        "close_approach_distance",
        "close_approach_distance_km",
        "close_approach_relative_velocity",
    ]

    assert (
        fact_set.facts[0].value
        == "2029-Apr-13 21:46"
    )

    assert fact_set.facts[1].unit == "AU"
    assert (
        fact_set.facts[1].value
        == 0.000254090910419299
    )

    assert fact_set.facts[2].unit == "km"
    assert fact_set.facts[2].value == 38000.0

    assert fact_set.facts[3].unit == "km/s"
    assert (
        fact_set.facts[3].value
        == 7.42253895678452
    )

    assert (
        fact_set.provenance
        == (source,)
    )


def test_close_approach_facts_preserve_event_index():
    approach_one = CloseApproach(
        object_id="asteroid:99942",
        designation="99942",
        fullname="99942 Apophis",
        close_approach_time="2029-Apr-13 21:46",
        distance_au=0.000254,
        distance_min_au=0.000253,
        distance_max_au=0.000255,
        distance_km=38000.0,
        distance_min_km=37900.0,
        distance_max_km=38100.0,
        relative_velocity_km_s=7.4,
        orbit_id="123",
        source=None,
    )

    approach_two = CloseApproach(
        object_id="asteroid:99942",
        designation="99942",
        fullname="99942 Apophis",
        close_approach_time="2036-Apr-13 12:00",
        distance_au=0.01,
        distance_min_au=0.009,
        distance_max_au=0.011,
        distance_km=1495978.7,
        distance_min_km=1346380.0,
        distance_max_km=1645577.0,
        relative_velocity_km_s=6.9,
        orbit_id="124",
        source=None,
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="close-approaches",
        result=(
            approach_one,
            approach_two,
        ),
    )

    fact_set = extract_ai_facts(
        "asteroid:99942",
        (result,),
    )

    assert len(fact_set.facts) == 8

    first_event = fact_set.facts[:4]
    second_event = fact_set.facts[4:]

    assert all(
        fact.metadata["index"] == 0
        for fact in first_event
    )

    assert all(
        fact.metadata["index"] == 1
        for fact in second_event
    )


def test_close_approach_does_not_invent_missing_source():
    approach = CloseApproach(
        object_id="asteroid:99942",
        designation="99942",
        fullname="99942 Apophis",
        close_approach_time="2029-Apr-13 21:46",
        distance_au=0.000254,
        distance_min_au=0.000253,
        distance_max_au=0.000255,
        distance_km=38000.0,
        distance_min_km=37900.0,
        distance_max_km=38100.0,
        relative_velocity_km_s=7.4,
        orbit_id=None,
        source=None,
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="close-approaches",
        result=(approach,),
    )

    fact_set = extract_ai_facts(
        "asteroid:99942",
        (result,),
    )

    assert len(fact_set.provenance) == 0
def test_scientific_facts_preserve_single_source():
    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=4.0,
            y=5.0,
            z=6.0,
            unit="AU/day",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(source,),
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    assert fact_set.facts[0].source == source
    assert fact_set.facts[1].source == source
    assert fact_set.facts[2].source == source
    assert fact_set.facts[3].source == source
    assert fact_set.facts[4].source == source
    assert fact_set.facts[5].source == source


def test_scientific_facts_do_not_guess_source_when_multiple_sources_exist():
    source_one = DataSource(
        name="Source One",
    )

    source_two = DataSource(
        name="Source Two",
    )

    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
        provenance=ScientificProvenance(
            sources=(source_one, source_two),
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    assert fact_set.facts[0].source is None
    assert fact_set.facts[1].source is None
    assert fact_set.facts[2].source is None

    assert fact_set.provenance == (
        source_one,
        source_two,
    )


def test_scientific_facts_have_no_source_without_provenance():
    scientific_data = ScientificData(
        object_id="earth",
        position=Position(
            x=1.0,
            y=2.0,
            z=3.0,
            unit="AU",
            frame="ICRF",
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    fact_set = extract_ai_facts(
        "earth",
        (result,),
    )

    assert fact_set.facts[0].source is None
    assert fact_set.provenance == ()


def test_extract_stellar_scientific_facts():
    source = DataSource(
        name="NASA Hubble Sirius Observation",
        provider="NASA Hubble Space Telescope",
    )

    scientific_data = ScientificData(
        object_id="sirius",
        observation=None,
        position=None,
        velocity=None,
        physical_properties={
            "mass_solar": 2.0,
        },
        orbital_properties=None,
        physical_properties_source=source,
        orbital_properties_source=None,
        stellar_properties={
            "system_type": "binary",
            "primary_component": "Sirius A",
            "companion_component": "Sirius B",
        },
        stellar_properties_source=source,
        provenance=ScientificProvenance(
            sources=(source,),
            reference_frames=(),
        ),
    )

    result = CapabilityExecutionResult(
        object_id="sirius",
        capability_id="scientific-data",
        result=scientific_data,
    )

    fact_set = extract_ai_facts(
        "sirius",
        (result,),
    )

    names = [fact.name for fact in fact_set.facts]

    assert names == [
        "physical_mass_solar",
        "stellar_system_type",
        "stellar_primary_component",
        "stellar_companion_component",
    ]

    assert fact_set.facts[0].value == 2.0
    assert fact_set.facts[1].value == "binary"
    assert fact_set.facts[2].value == "Sirius A"
    assert fact_set.facts[3].value == "Sirius B"

    assert all(
        fact.source_capability == "scientific-data"
        for fact in fact_set.facts
    )

    assert all(
        fact.source == source
        for fact in fact_set.facts
    )

    assert fact_set.provenance == (source,)


def test_extract_earth_object_graph_facts():
    from astrosphere.ai.context import AIContext
    from astrosphere.ai.grounding import build_ai_context

    context = build_ai_context(
        "What is Earth's place in the Solar System?",
        "earth",
    )

    fact_set = extract_ai_facts(
        "earth",
        (),
        context.object_graph,
    )

    graph_facts = [
        fact
        for fact in fact_set.facts
        if fact.source_capability == "relationships"
    ]

    assert [
        fact.name
        for fact in graph_facts
    ] == [
        "object_parent",
        "object_ancestor",
        "object_ancestor",
        "object_ancestor",
        "object_ancestor",
        "object_child",
        "object_child",
        "relationship_orbits",
        "relationship_contains",
        "relationship_contains",
    ]

    assert graph_facts[0].value == "sun"

    assert [
        fact.value
        for fact in graph_facts[1:5]
    ] == [
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]

    assert {
        fact.value
        for fact in graph_facts[5:7]
    } == {
        "moon",
        "spacecraft:25544",
    }

    assert graph_facts[7].value == "sun"

    assert {
        fact.value
        for fact in graph_facts[8:]
    } == {
        "moon",
        "spacecraft:25544",
    }


def test_extract_milky_way_object_graph_facts():
    from astrosphere.ai.grounding import build_ai_context

    context = build_ai_context(
        "What is the Milky Way?",
        "milky-way",
    )

    fact_set = extract_ai_facts(
        "milky-way",
        (),
        context.object_graph,
    )

    graph_facts = [
        fact
        for fact in fact_set.facts
        if fact.source_capability == "relationships"
    ]

    assert graph_facts[0].name == "object_parent"
    assert graph_facts[0].value == "universe"

    ancestor_facts = [
        fact
        for fact in graph_facts
        if fact.name == "object_ancestor"
    ]

    assert [
        fact.value
        for fact in ancestor_facts
    ] == [
        "universe",
    ]

    child_values = {
        fact.value
        for fact in graph_facts
        if fact.name == "object_child"
    }

    assert child_values == {
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    }

    relationship_facts = [
        fact
        for fact in graph_facts
        if fact.name.startswith("relationship_")
    ]

    assert [
        (
            fact.name,
            fact.value,
        )
        for fact in relationship_facts
    ] == [
        (
            "relationship_member_of",
            "universe",
        ),
        (
            "relationship_contains",
            "solar-system",
        ),
        (
            "relationship_contains",
            "sirius",
        ),
        (
            "relationship_contains",
            "proxima-centauri",
        ),
        (
            "relationship_contains",
            "betelgeuse",
        ),
        (
            "relationship_contains",
            "vega",
        ),
    ]


def test_graph_facts_have_no_external_provenance():
    from astrosphere.ai.grounding import build_ai_context

    context = build_ai_context(
        "What does Earth orbit?",
        "earth",
    )

    fact_set = extract_ai_facts(
        "earth",
        (),
        context.object_graph,
    )

    assert fact_set.provenance == ()

    assert all(
        fact.source is None
        for fact in fact_set.facts
        if fact.source_capability == "relationships"
    )
