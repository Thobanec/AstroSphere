from astrosphere.ai import (
    AIResponse,
    build_ai_context,
    compose_ai_response,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)
from astrosphere.models.scientific import (
    DataSource,
    Position,
    ScientificData,
    ScientificProvenance,
)


def test_compose_single_capability_response():
    context = build_ai_context(
        "What is the current position of Apophis?",
        "asteroid:99942",
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "designation": "99942",
            "status": "success",
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert isinstance(response, AIResponse)
    assert response.question == (
        "What is the current position of Apophis?"
    )
    assert response.object_id == "asteroid:99942"
    assert "tracking" in response.answer
    assert "Apophis" in response.answer
    assert response.results == (result,)


def test_compose_multiple_capability_results():
    context = build_ai_context(
        "Show the position and trajectory of Apophis.",
        "asteroid:99942",
    )

    tracking_result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "status": "success",
        },
    )

    trajectory_result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="trajectory",
        result={
            "status": "success",
            "samples": 181,
        },
    )

    response = compose_ai_response(
        context,
        (
            tracking_result,
            trajectory_result,
        ),
    )

    assert response.results == (
        tracking_result,
        trajectory_result,
    )
    assert response.results[0].capability_id == "tracking"
    assert response.results[1].capability_id == "trajectory"
    assert "tracking" in response.answer
    assert "trajectory" in response.answer


def test_compose_preserves_grounded_provenance():
    context = build_ai_context(
        "What scientific data is available for Earth?",
        "earth",
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result={
            "status": "success",
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    source_names = tuple(
        source.name
        for source in response.provenance
    )

    assert "JPL DE440S" in source_names
    assert "JPL Planetary Physical Parameters" in source_names


def test_compose_collects_result_provenance():
    context = build_ai_context(
        "What is the current position of Apophis?",
        "asteroid:99942",
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "status": "success",
            "provenance": context.provenance,
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.provenance == context.provenance


def test_compose_rejects_invalid_results():
    context = build_ai_context(
        "What is Apophis?",
        "asteroid:99942",
    )

    try:
        compose_ai_response(
            context,
            ("invalid-result",),
        )
    except ValueError as exc:
        assert "CapabilityExecutionResult" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid capability result to be rejected."
        )


def test_compose_empty_results():
    context = build_ai_context(
        "What is Apophis?",
        "asteroid:99942",
    )

    response = compose_ai_response(
        context,
        (),
    )

    assert isinstance(response, AIResponse)
    assert response.results == ()
    assert "No capability results" in response.answer


def test_compose_renders_scientific_facts():
    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
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
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.facts is not None
    assert len(response.facts.facts) == 6

    assert "position_x: 1.0 AU" in response.answer
    assert "position_y: 2.0 AU" in response.answer
    assert "position_z: 3.0 AU" in response.answer
    assert "velocity_x: 4.0 AU/day" in response.answer


def test_compose_renders_space_weather_facts():
    context = build_ai_context(
        "What is the current solar wind speed?",
        "earth",
    )

    weather = SpaceWeatherData(
        observation_time=(
            "2026-09-16T10:00:00+00:00"
        ),
        solar_wind=SolarWind(
            speed_km_s=450.0,
            density_cm3=5.0,
        ),
        magnetic_field=MagneticField(
            bt_nt=6.0,
            bz_nt=-2.5,
        ),
        geomagnetic=Geomagnetic(
            kp=3.0,
        ),
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="space-weather",
        result=weather,
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.facts is not None
    assert len(response.facts.facts) == 5

    assert "solar_wind_speed: 450.0 km/s" in (
        response.answer
    )

    assert "solar_wind_density: 5.0 cm^-3" in (
        response.answer
    )

    assert "magnetic_field_bz_gsm: -2.5 nT" in (
        response.answer
    )

    assert "geomagnetic_kp: 3.0" in response.answer


def test_compose_does_not_invent_facts():
    context = build_ai_context(
        "What is Apophis?",
        "asteroid:99942",
    )

    result = CapabilityExecutionResult(
        object_id="asteroid:99942",
        capability_id="tracking",
        result={
            "status": "success",
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.facts is not None
    assert response.facts.facts == ()

    assert "position_x" not in response.answer
    assert "velocity_x" not in response.answer
from astrosphere.models.scientific import (
    Geomagnetic,
    MagneticField,
    Position,
    ScientificData,
    SolarWind,
    SpaceWeatherData,
    Velocity,
)
from astrosphere.ai.context import AIContext
from astrosphere.ai.fact_extractor import extract_ai_facts
from astrosphere.ai.interpreter import interpret_ai_facts
from astrosphere.ai.response import AIResponse
from astrosphere.ai.response_composer import compose_ai_response
from astrosphere.capabilities.results import CapabilityExecutionResult
from astrosphere.models.scientific import (
    Position,
    ScientificData,
    Velocity,
)


def test_compose_attaches_interpretations():
    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
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
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.interpretations is not None
    assert response.interpretations.object_id == "earth"
    assert len(response.interpretations.interpretations) == 6

    first = response.interpretations.interpretations[0]

    assert first.subject == "Earth"
    assert first.statement == (
        "Earth position_x is 1.0 AU."
    )
    assert first.supporting_facts == (
        "position_x",
    )
def test_compose_preserves_interpretation_traceability():
    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
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
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    interpretation = (
        response.interpretations.interpretations[0]
    )

    assert interpretation.supporting_facts == (
        "position_x",
    )

    assert interpretation.supporting_capabilities == (
        "scientific-data",
    )
def test_compose_preserves_fact_provenance():
    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
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

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    interpretation = (
        response.interpretations.interpretations[0]
    )

    assert interpretation.provenance == (
        source,
    )

def test_compose_uses_language_provider():
    from astrosphere.ai.llm import (
        AILanguageResponse,
    )

    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
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
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    class TestProvider:
        def __init__(self):
            self.request = None

        def generate(self, request):
            self.request = request

            return AILanguageResponse(
                answer="LLM boundary response."
            )

    provider = TestProvider()

    response = compose_ai_response(
        context,
        (result,),
        language_provider=provider,
    )

    assert response.answer == (
        "LLM boundary response."
    )

    assert provider.request is not None
    assert provider.request.question == (
        "What is the current position of Earth?"
    )
    assert provider.request.object.id == "earth"
    assert provider.request.facts.object_id == "earth"
    assert len(provider.request.facts.facts) == 6
    assert provider.request.interpretations.object_id == (
        "earth"
    )


def test_compose_preserves_astrosphere_provenance_with_language_provider():
    from astrosphere.ai.llm import (
        AILanguageResponse,
    )

    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
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

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result=scientific_data,
    )

    class TestProvider:
        def generate(self, request):
            return AILanguageResponse(
                answer="Generated language."
            )

    response = compose_ai_response(
        context,
        (result,),
        language_provider=TestProvider(),
    )

    assert source in response.provenance


def test_compose_without_provider_preserves_deterministic_answer():
    context = build_ai_context(
        "What is the current position of Earth?",
        "earth",
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="scientific-data",
        result={
            "status": "success",
        },
    )

    response = compose_ai_response(
        context,
        (result,),
    )

    assert response.answer == (
        "AstroSphere retrieved the "
        "scientific-data result for Earth."
    )
