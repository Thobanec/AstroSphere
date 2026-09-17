from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretation,
    AIInterpretationSet,
)
from astrosphere.ai.llm import (
    AILanguageRequest,
    AILanguageResponse,
    AILanguageProvider,
)
from astrosphere.models.celestial import (
    CelestialObject,
)
from astrosphere.models.scientific import (
    DataSource,
)


def test_language_request_preserves_grounded_context():
    obj = CelestialObject(
        id="earth",
        name="Earth",
        object_type="planet",
    )

    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    facts = AIFactSet(
        object_id="earth",
        facts=(
            AIFact(
                name="position_x",
                value=1.0,
                unit="AU",
                source_capability="scientific-data",
                source=source,
            ),
        ),
        provenance=(source,),
    )

    interpretations = AIInterpretationSet(
        object_id="earth",
        interpretations=(
            AIInterpretation(
                subject="Earth",
                statement="Earth has a measured position.",
                supporting_facts=("position_x",),
                supporting_capabilities=("scientific-data",),
                provenance=(source,),
            ),
        ),
        provenance=(source,),
    )

    request = AILanguageRequest(
        question="What is the current position of Earth?",
        object=obj,
        facts=facts,
        interpretations=interpretations,
        provenance=(source,),
        uncertainties=("Example uncertainty",),
        observation_time="2026-09-17T00:00:00Z",
    )

    assert request.question == (
        "What is the current position of Earth?"
    )
    assert request.object.id == "earth"
    assert request.facts == facts
    assert request.interpretations == interpretations
    assert request.provenance == (source,)
    assert request.uncertainties == (
        "Example uncertainty",
    )
    assert request.observation_time == (
        "2026-09-17T00:00:00Z"
    )


def test_language_response_preserves_answer():
    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    response = AILanguageResponse(
        answer="Earth's position is based on the supplied scientific data.",
        provenance=(source,),
        uncertainties=("Example uncertainty",),
    )

    assert response.answer == (
        "Earth's position is based on the supplied scientific data."
    )
    assert response.provenance == (source,)
    assert response.uncertainties == (
        "Example uncertainty",
    )


def test_language_provider_protocol_accepts_compatible_provider():
    class TestProvider:
        def generate(
            self,
            request: AILanguageRequest,
        ) -> AILanguageResponse:
            return AILanguageResponse(
                answer=(
                    f"Answered from grounded facts for "
                    f"{request.object.name}."
                )
            )

    provider: AILanguageProvider = TestProvider()

    request = AILanguageRequest(
        question="Describe Earth.",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "Answered from grounded facts for Earth."
    )


def test_language_request_is_immutable():
    request = AILanguageRequest(
        question="Describe Earth.",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    try:
        request.question = "Changed."
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "AILanguageRequest must be immutable."
        )


def test_language_response_is_immutable():
    response = AILanguageResponse(
        answer="Grounded response.",
    )

    try:
        response.answer = "Changed."
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "AILanguageResponse must be immutable."
        )
