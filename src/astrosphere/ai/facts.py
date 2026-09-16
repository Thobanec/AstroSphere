from dataclasses import dataclass
from typing import Any

from astrosphere.models.scientific import (
    DataSource,
)


@dataclass(frozen=True)
class AIFact:
    name: str
    value: Any
    unit: str | None = None
    source_capability: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class AIFactSet:
    object_id: str
    facts: tuple[AIFact, ...] = ()
    observation_time: Any | None = None
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
