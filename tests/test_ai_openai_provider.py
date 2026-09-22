from types import SimpleNamespace

from astrosphere.ai.explanation import (
    AIExplanation,
    AIExplanationSet,
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
from astrosphere.ai.openai_provider import (
    OpenAILanguageProvider,
)
from astrosphere.ai.provider_config import (
    AIProviderConfig,
)
from astrosphere.models.celestial import (
    CelestialObject,
)
from astrosphere.models.scientific import (
    DataSource,
)


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)

        return SimpleNamespace(
            output_text=(
                "Earth is described using the supplied "
                "AstroSphere scientific data."
            )
        )


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


def _build_request(source=None):
    provenance = (source,) if source is not None else ()

    return AILanguageRequest(
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
                    source=source,
                ),
            ),
            provenance=provenance,
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
        provenance=provenance,
        uncertainties=("Example uncertainty",),
        observation_time="2026-09-17T00:00:00Z",
    )


def test_openai_provider_generates_response_from_fake_client():
    client = FakeOpenAIClient()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    response = provider.generate(
        _build_request(),
    )

    assert response.answer == (
        "Earth is described using the supplied "
        "AstroSphere scientific data."
    )


def test_openai_provider_uses_configured_model():
    client = FakeOpenAIClient()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    provider.generate(
        _build_request(),
    )

    assert client.responses.calls[0]["model"] == (
        "test-model"
    )


def test_openai_provider_sends_grounded_question_and_facts():
    client = FakeOpenAIClient()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    provider.generate(
        _build_request(),
    )

    call = client.responses.calls[0]

    assert call["input"].startswith(
        "Question:\n"
        "What is the position of Earth?"
    )
    assert "position_x: 1.5 AU" in call["input"]
    assert "Earth (earth)" in call["input"]
    assert "2026-09-17T00:00:00Z" in call["input"]


def test_openai_provider_sends_grounding_instructions():
    client = FakeOpenAIClient()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    provider.generate(
        _build_request(),
    )

    instructions = client.responses.calls[0][
        "instructions"
    ]

    assert "Use only the supplied AstroSphere facts" in (
        instructions
    )
    assert "Do not invent scientific measurements" in (
        instructions
    )
    assert "Preserve uncertainty" in instructions


def test_openai_provider_preserves_astrosphere_provenance():
    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    client = FakeOpenAIClient()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    response = provider.generate(
        _build_request(source),
    )

    assert response.provenance == (source,)
    assert response.uncertainties == (
        "Example uncertainty",
    )


def test_openai_provider_rejects_missing_api_key_without_client():
    config = AIProviderConfig(
        api_key=None,
        model="test-model",
    )

    try:
        OpenAILanguageProvider(
            config=config,
        )
    except ValueError as exc:
        assert str(exc) == (
            "OPENAI_API_KEY is required for "
            "OpenAILanguageProvider."
        )
    else:
        raise AssertionError(
            "Missing API keys must be rejected."
        )


def test_openai_provider_rejects_invalid_language_request():
    client = FakeOpenAIClient()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

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

def test_openai_provider_is_compatible_with_language_provider_protocol():
    from astrosphere.ai.llm import AILanguageProvider

    client = FakeOpenAIClient()

    provider: AILanguageProvider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    response = provider.generate(
        _build_request(),
    )

    assert response.answer == (
        "Earth is described using the supplied "
        "AstroSphere scientific data."
    )


def test_openai_provider_preserves_grounded_request_data():
    client = FakeOpenAIClient()

    request = _build_request()

    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=client,
    )

    provider.generate(request)

    call = client.responses.calls[0]

    assert request.question == (
        "What is the position of Earth?"
    )
    assert request.object.id == "earth"
    assert request.facts.facts[0].name == (
        "position_x"
    )
    assert request.facts.facts[0].value == 1.5
    assert request.observation_time == (
        "2026-09-17T00:00:00Z"
    )

def test_openai_provider_includes_educational_explanations():
    provider = OpenAILanguageProvider(
        config=AIProviderConfig(
            api_key="test-key",
            model="test-model",
        ),
        client=FakeOpenAIClient(),
    )

    explanation = AIExplanation(
        subject="velocity",
        explanation=(
            "Velocity describes how an object's position "
            "changes over time."
        ),
        level="beginner",
        explanation_type="what",
    )

    request = AILanguageRequest(
        question="What is velocity?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="velocity_x",
                    value=5.0,
                    unit="km/s",
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
        explanations=AIExplanationSet(
            object_id="earth",
            explanations=(explanation,),
            level="beginner",
        ),
    )

    provider.generate(request)

    call = provider.client.responses.calls[-1]

    assert "Educational explanations:" in call["input"]
    assert "velocity (what, beginner)" in call["input"]
    assert (
        "Velocity describes how an object's position "
        "changes over time."
        in call["input"]
    )
    assert "velocity_x: 5.0 km/s" in call["input"]
