from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AIProviderConfig:
    api_key: str | None = None
    model: str = "gpt-5.4-mini"

    @classmethod
    def from_environment(cls):
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-5.4-mini",
            ),
        )
