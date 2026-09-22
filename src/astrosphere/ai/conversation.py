from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AssistantMessage:
    role: str
    content: str
    object_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIConversation:
    conversation_id: str
    messages: tuple[AssistantMessage, ...] = ()
    object_id: str | None = None
