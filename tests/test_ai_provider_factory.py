from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.ai.openai_provider import (
    OpenAILanguageProvider,
)
from astrosphere.ai.provider_factory import (
    create_language_provider,
)
from astrosphere.ai.provider_config import (
    AIProviderConfig,
)


class FakeResponses:
    def create(self, **kwargs):
        class FakeResponse:
            output_text = "Test response."

        return FakeResponse()


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_factory_defaults_to_deterministic_provider(
    monkeypatch,
):
    monkeypatch.delenv(
        "ASTROSPHERE_AI_PROVIDER",
        raising=False,
    )

    provider = create_language_provider()

    assert isinstance(
        provider,
        DeterministicLanguageProvider,
    )


def test_factory_creates_deterministic_provider():
    provider = create_language_provider(
        provider_name="deterministic",
    )

    assert isinstance(
        provider,
        DeterministicLanguageProvider,
    )


def test_factory_creates_openai_provider():
    provider = create_language_provider(
        provider_name="openai",
        config=AIProviderConfig(
            api_key="test-api-key",
            model="test-model",
        ),
        client=FakeOpenAIClient(),
    )

    assert isinstance(
        provider,
        OpenAILanguageProvider,
    )


def test_factory_reads_provider_from_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "deterministic",
    )

    provider = create_language_provider()

    assert isinstance(
        provider,
        DeterministicLanguageProvider,
    )


def test_factory_normalizes_provider_name(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "  DETERMINISTIC  ",
    )

    provider = create_language_provider()

    assert isinstance(
        provider,
        DeterministicLanguageProvider,
    )


def test_factory_rejects_unsupported_provider():
    try:
        create_language_provider(
            provider_name="unsupported",
        )
    except ValueError as exc:
        assert str(exc) == (
            "Unsupported AI language provider: "
            "unsupported"
        )
    else:
        raise AssertionError(
            "Unsupported providers must be rejected."
        )


def test_explicit_provider_overrides_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "ASTROSPHERE_AI_PROVIDER",
        "openai",
    )

    provider = create_language_provider(
        provider_name="deterministic",
    )

    assert isinstance(
        provider,
        DeterministicLanguageProvider,
    )
