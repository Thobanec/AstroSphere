from astrosphere.ai.provider_config import AIProviderConfig


def test_provider_config_has_safe_defaults():
    config = AIProviderConfig()

    assert config.api_key is None
    assert config.model == "gpt-5.4-mini"


def test_provider_config_reads_api_key_from_environment(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-api-key",
    )

    config = AIProviderConfig.from_environment()

    assert config.api_key == "test-api-key"


def test_provider_config_reads_model_from_environment(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )

    config = AIProviderConfig.from_environment()

    assert config.model == "test-model"


def test_provider_config_uses_default_model_when_environment_is_missing(
    monkeypatch,
):
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )

    config = AIProviderConfig.from_environment()

    assert config.model == "gpt-5.4-mini"


def test_provider_config_is_immutable():
    config = AIProviderConfig()

    try:
        config.model = "changed"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "AIProviderConfig must be immutable."
        )
