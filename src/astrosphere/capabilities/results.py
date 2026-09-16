from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilityExecutionResult:
    object_id: str
    capability_id: str
    result: Any
    metadata: dict[str, Any] | None = None
