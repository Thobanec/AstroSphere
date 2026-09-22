from dataclasses import dataclass
from typing import Any

from astrosphere.capabilities.definitions import CapabilityDefinition
from astrosphere.capabilities.results import CapabilityExecutionResult
from astrosphere.models.celestial import CelestialObject
from astrosphere.models.relationship import ScientificRelationship
from astrosphere.models.scientific import DataSource, ScientificData


@dataclass(frozen=True)
class AIObjectGraph:
    object: CelestialObject
    parent: CelestialObject | None = None
    ancestors: tuple[CelestialObject, ...] = ()
    children: tuple[CelestialObject, ...] = ()
    relationships: tuple[ScientificRelationship, ...] = ()
    incoming_relationships: tuple[ScientificRelationship, ...] = ()


@dataclass(frozen=True)
class AIContext:
    question: str
    observation_time: str | None = None
    object: CelestialObject | None = None
    scientific_data: ScientificData | None = None
    capabilities: tuple[CapabilityDefinition, ...] = ()
    capability_results: tuple[CapabilityExecutionResult, ...] = ()
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
    object_graph: AIObjectGraph | None = None
    metadata: dict[str, Any] | None = None
