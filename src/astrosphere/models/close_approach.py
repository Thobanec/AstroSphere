from dataclasses import dataclass

from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class CloseApproach:
    object_id: str
    designation: str
    fullname: str
    close_approach_time: str
    distance_au: float
    distance_min_au: float
    distance_max_au: float
    distance_km: float
    distance_min_km: float
    distance_max_km: float
    relative_velocity_km_s: float
    orbit_id: str | None = None
    source: DataSource | None = None
