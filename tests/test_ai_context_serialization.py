from astrosphere.ai import build_ai_context
from astrosphere.ai.context_serialization import (
    ai_context_to_dict,
)


def test_ai_context_to_dict_serializes_grounded_earth_context():
    context = build_ai_context(
        "Where is Earth?",
        "earth",
    )

    data = ai_context_to_dict(context)

    assert data["question"] == "Where is Earth?"
    assert data["object"]["id"] == "earth"
    assert data["object"]["name"] == "Earth"

    assert data["scientific_data"] is not None
    assert data["scientific_data"]["object_id"] == "earth"

    capability_ids = {
        capability["id"]
        for capability in data["capabilities"]
    }

    assert "context" in capability_ids
    assert "scientific-data" in capability_ids
    assert "relationships" in capability_ids

    assert data["object_graph"]["object"]["id"] == "earth"
    assert data["object_graph"]["parent"]["id"] == "sun"

    ancestor_ids = [
        ancestor["id"]
        for ancestor in data["object_graph"]["ancestors"]
    ]

    assert ancestor_ids == [
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]

    relationship_types = {
        (
            relationship["relationship_type"],
            relationship["target_id"],
        )
        for relationship
        in data["object_graph"]["relationships"]
    }

    assert ("orbits", "sun") in relationship_types


def test_ai_context_to_dict_serializes_milky_way_stellar_graph():
    context = build_ai_context(
        "What is in the Milky Way?",
        "milky-way",
    )

    data = ai_context_to_dict(context)

    assert data["object"]["id"] == "milky-way"

    child_ids = {
        child["id"]
        for child in data["object_graph"]["children"]
    }

    assert {
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    } <= child_ids


def test_ai_context_to_dict_serializes_stellar_scientific_data():
    context = build_ai_context(
        "What is Sirius?",
        "sirius",
    )

    data = ai_context_to_dict(context)

    assert data["object"]["id"] == "sirius"

    scientific_data = data["scientific_data"]

    assert scientific_data is not None
    assert scientific_data["physical_properties"]
    assert scientific_data["stellar_properties"]

    provenance_names = {
        source["name"]
        for source in data["provenance"]
    }

    assert "NASA Hubble Sirius Observation" in provenance_names


def test_ai_context_to_dict_serializes_empty_optional_fields():
    context = build_ai_context(
        "What is the Moon?",
        "moon",
    )

    data = ai_context_to_dict(context)

    assert data["object"]["id"] == "moon"
    assert data["scientific_data"] is None
    assert data["provenance"] == []
    assert data["capability_results"] == []
    assert data["metadata"] is None


def test_ai_context_to_dict_rejects_invalid_context():
    try:
        ai_context_to_dict(None)
    except ValueError as exc:
        assert str(exc) == "AIContext is required."
    else:
        raise AssertionError(
            "Expected ValueError for invalid AIContext."
        )

def test_capability_result_serializes_nested_celestial_objects():
    from astrosphere.capabilities.results import (
        CapabilityExecutionResult,
    )
    from astrosphere.models.celestial_registry import (
        get_celestial_object,
    )
    from astrosphere.ai.context_serialization import (
        _capability_result_to_dict,
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="context",
        result={
            "object": get_celestial_object("earth"),
            "parent": get_celestial_object("sun"),
        },
    )

    serialized = _capability_result_to_dict(result)

    assert serialized["object_id"] == "earth"
    assert serialized["capability_id"] == "context"

    assert serialized["result"]["object"]["id"] == "earth"
    assert serialized["result"]["object"]["name"] == "Earth"

    assert serialized["result"]["parent"]["id"] == "sun"
    assert serialized["result"]["parent"]["name"] == "Sun"


def test_capability_result_serializes_datetime():
    from datetime import datetime, timezone

    from astrosphere.capabilities.results import (
        CapabilityExecutionResult,
    )
    from astrosphere.ai.context_serialization import (
        _capability_result_to_dict,
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="planetary-trajectory",
        result=[
            {
                "date": datetime(
                    2026,
                    9,
                    21,
                    12,
                    0,
                    tzinfo=timezone.utc,
                ),
                "x_au": 1.0,
                "y_au": 2.0,
                "z_au": 3.0,
            }
        ],
    )

    serialized = _capability_result_to_dict(result)

    assert (
        serialized["result"][0]["date"]
        == "2026-09-21T12:00:00+00:00"
    )

    assert serialized["result"][0]["x_au"] == 1.0


def test_capability_result_serializes_space_weather():
    from astrosphere.capabilities.results import (
        CapabilityExecutionResult,
    )
    from astrosphere.models.scientific import (
        DataSource,
        Geomagnetic,
        MagneticField,
        ScientificProvenance,
        SolarWind,
        SpaceWeatherData,
    )
    from astrosphere.ai.context_serialization import (
        _capability_result_to_dict,
    )

    weather = SpaceWeatherData(
        observation_time="2026-09-21T13:50:00+00:00",
        solar_wind=SolarWind(
            speed_km_s=328.6,
            density_cm3=1.41,
            temperature_k=58094.0,
        ),
        magnetic_field=MagneticField(
            bt_nt=4.28,
            bz_nt=-0.9,
        ),
        geomagnetic=Geomagnetic(
            kp=0.67,
        ),
        provenance=ScientificProvenance(
            sources=(
                DataSource(
                    name="NOAA Space Weather Prediction Center",
                    provider="NOAA SWPC",
                    url="https://services.swpc.noaa.gov",
                    dataset=(
                        "Real-Time Solar Wind and "
                        "Geomagnetic Data"
                    ),
                ),
            ),
            reference_frames=("GSM",),
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="space-weather",
        result=weather,
    )

    serialized = _capability_result_to_dict(result)

    assert (
        serialized["result"]["observation_time"]
        == "2026-09-21T13:50:00+00:00"
    )

    assert (
        serialized["result"]["solar_wind"]["speed_km_s"]
        == 328.6
    )

    assert (
        serialized["result"]["magnetic_field"]["bz_nt"]
        == -0.9
    )

    assert (
        serialized["result"]["geomagnetic"]["kp"]
        == 0.67
    )

    assert (
        serialized["result"]["provenance"]["sources"][0]["name"]
        == "NOAA Space Weather Prediction Center"
    )
