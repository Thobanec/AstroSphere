from dataclasses import dataclass

from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class PlanetaryScientificProperties:
    object_id: str
    source: DataSource
    physical_properties: dict
    orbital_properties: dict
