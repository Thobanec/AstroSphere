from dataclasses import dataclass
from typing import Any

from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class AIExplanation:
    subject: str
    explanation: str
    level: str = "standard"
    explanation_type: str = "what"
    supporting_facts: tuple[str, ...] = ()
    supporting_interpretations: tuple[str, ...] = ()
    observation_time: Any | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()


@dataclass(frozen=True)
class AIExplanationSet:
    object_id: str
    explanations: tuple[AIExplanation, ...] = ()
    level: str = "standard"
    explanation_type: str = "what"
    observation_time: Any | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
