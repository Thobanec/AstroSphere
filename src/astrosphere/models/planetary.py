from dataclasses import dataclass


@dataclass
class PlanetaryObject:
    name: str
    skyfield_name: str