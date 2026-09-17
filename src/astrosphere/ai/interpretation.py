from dataclasses import dataclass
from typing import Any

from astrosphere.models.scientific import (
    DataSource,
)


@dataclass(frozen=True)
class AIInterpretation:
    subject: str
    statement: str
    supporting_facts: tuple[str, ...] = ()
    supporting_capabilities: tuple[str, ...] = ()
    observation_time: Any | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()


@dataclass(frozen=True)
class AIInterpretationSet:
    object_id: str
    interpretations: tuple[AIInterpretation, ...] = ()
    observation_time: Any | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
