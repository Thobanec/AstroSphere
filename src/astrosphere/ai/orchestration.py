from dataclasses import dataclass
from typing import Any

from astrosphere.ai.facts import AIFactSet
from astrosphere.ai.interpretation import AIInterpretationSet
from astrosphere.models.scientific import DataSource
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


@dataclass(frozen=True)
class AICapabilityPlanItem:
    capability_id: str
    reason: str
    parameters: dict[str, Any] | None = None
    execution_order: int = 0


@dataclass(frozen=True)
class AIOrchestrationRequest:
    question: str
    object_id: str
    capability_ids: tuple[str, ...] = ()
    observation_time: Any | None = None
    parameters: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIOrchestrationResult:
    question: str
    object_id: str
    answer: str
    capabilities: tuple[str, ...] = ()
    results: tuple[CapabilityExecutionResult, ...] = ()
    facts: AIFactSet | None = None
    interpretations: AIInterpretationSet | None = None
    observation_time: Any | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
