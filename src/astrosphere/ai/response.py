from dataclasses import dataclass
from typing import Any

from astrosphere.ai.facts import AIFactSet
from astrosphere.ai.interpretation import AIInterpretationSet
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)
from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class AIResponse:
    question: str
    object_id: str
    answer: str
    observation_time: Any | None = None
    results: tuple[CapabilityExecutionResult, ...] = ()
    facts: AIFactSet | None = None
    interpretations: AIInterpretationSet | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
