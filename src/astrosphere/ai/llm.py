from dataclasses import dataclass
from typing import Any, Protocol

from astrosphere.ai.facts import AIFactSet
from astrosphere.ai.interpretation import AIInterpretationSet
from astrosphere.models.celestial import CelestialObject
from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class AILanguageRequest:
    question: str
    object: CelestialObject
    facts: AIFactSet
    interpretations: AIInterpretationSet
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()
    observation_time: Any | None = None


@dataclass(frozen=True)
class AILanguageResponse:
    answer: str
    provenance: tuple[DataSource, ...] = ()
    uncertainties: tuple[str, ...] = ()


class AILanguageProvider(Protocol):
    def generate(
        self,
        request: AILanguageRequest,
    ) -> AILanguageResponse:
        ...
