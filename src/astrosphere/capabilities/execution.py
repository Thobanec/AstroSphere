from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilityExecutionRequest:
    object_id: str
    capability_id: str
    observation_time: str | None = None
    parameters: dict[str, Any] | None = None
