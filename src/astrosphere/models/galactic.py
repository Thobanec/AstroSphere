from dataclasses import dataclass

from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class GalacticCoordinate:
    longitude_deg: float
    latitude_deg: float
    distance_pc: float | None = None
    frame: str = "galactic"
    origin: str = "sun"
    source: DataSource | None = None
