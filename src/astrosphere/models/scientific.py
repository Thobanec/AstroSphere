from dataclasses import dataclass


@dataclass(frozen=True)
class DataSource:
    name: str
    provider: str | None = None
    url: str | None = None
    dataset: str | None = None
    version: str | None = None
    upstream_source: str | None = None


@dataclass(frozen=True)
class Observation:
    observation_time: str
    source: DataSource | None = None


@dataclass(frozen=True)
class Position:
    x: float
    y: float
    z: float
    unit: str
    frame: str


@dataclass(frozen=True)
class Velocity:
    x: float
    y: float
    z: float
    unit: str
    frame: str


@dataclass(frozen=True)
class ScientificProvenance:
    sources: tuple[DataSource, ...] = ()
    reference_frames: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScientificData:
    object_id: str
    observation: Observation | None = None
    position: Position | None = None
    velocity: Velocity | None = None
    physical_properties: dict | None = None
    orbital_properties: dict | None = None
    physical_properties_source: DataSource | None = None
    orbital_properties_source: DataSource | None = None
    provenance: ScientificProvenance | None = None

@dataclass(frozen=True)
class SolarWind:
    speed_km_s: float | None = None
    density_cm3: float | None = None
    temperature_k: float | None = None


@dataclass(frozen=True)
class MagneticField:
    bt_nt: float | None = None
    bz_nt: float | None = None


@dataclass(frozen=True)
class Geomagnetic:
    kp: float | None = None


@dataclass(frozen=True)
class SpaceWeatherData:
    observation_time: str
    solar_wind: SolarWind | None = None
    magnetic_field: MagneticField | None = None
    geomagnetic: Geomagnetic | None = None
    provenance: ScientificProvenance | None = None
