from dataclasses import dataclass

from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class StellarScientificProperties:
    object_id: str
    source: DataSource
    physical_properties: dict
    stellar_properties: dict
