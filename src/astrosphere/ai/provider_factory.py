import os

from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.ai.llm import (
    AILanguageProvider,
)
from astrosphere.ai.openai_provider import (
    OpenAILanguageProvider,
)
from astrosphere.ai.provider_config import (
    AIProviderConfig,
)


def create_language_provider(
    provider_name: str | None = None,
    config: AIProviderConfig | None = None,
    client=None,
) -> AILanguageProvider:
    selected_provider = (
        provider_name
        if provider_name is not None
        else os.getenv(
            "ASTROSPHERE_AI_PROVIDER",
            "deterministic",
        )
    ).strip().lower()

    if selected_provider == "deterministic":
        return DeterministicLanguageProvider()

    if selected_provider == "openai":
        return OpenAILanguageProvider(
            config=config,
            client=client,
        )

    raise ValueError(
        f"Unsupported AI language provider: "
        f"{selected_provider}"
    )
