from dataclasses import dataclass

from astrosphere.ai.intent import (
    AICapabilityIntent,
)


@dataclass(frozen=True)
class AIScientificQuestion:
    question: str
    object_id: str | None = None
    requested_information: tuple[str, ...] = ()
    temporal_context: str | None = None
    temporal_contexts: tuple[tuple[str, str], ...] = ()
    intents: tuple[AICapabilityIntent, ...] = ()
