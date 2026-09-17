from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretationSet,
)
from astrosphere.ai.llm import (
    AILanguageRequest,
)
from astrosphere.models.celestial import (
    CelestialObject,
)
from astrosphere.models.scientific import (
    DataSource,
)


def test_deterministic_provider_renders_grounded_facts():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="What is the position of Earth?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="position_x",
                    value=1.5,
                    unit="AU",
                    source_capability="scientific-data",
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "Grounded scientific information for Earth:\n"
        "position_x: 1.5 AU"
    )


def test_deterministic_provider_preserves_provenance():
    provider = DeterministicLanguageProvider()

    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

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
        provenance=(source,),
        uncertainties=("Example uncertainty",),
    )

    response = provider.generate(request)

    assert response.provenance == (source,)
    assert response.uncertainties == (
        "Example uncertainty",
    )


def test_deterministic_provider_handles_empty_facts():
    provider = DeterministicLanguageProvider()

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
        "No grounded scientific facts are "
        "available for Earth."
    )


def test_deterministic_provider_rejects_invalid_request():
    provider = DeterministicLanguageProvider()

    try:
        provider.generate(None)
    except ValueError as exc:
        assert str(exc) == (
            "AILanguageRequest is required."
        )
    else:
        raise AssertionError(
            "Invalid language requests must be rejected."
        )
