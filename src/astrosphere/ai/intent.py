from dataclasses import dataclass


@dataclass(frozen=True)
class AICapabilityIntent:
    capability_id: str
    reason: str
