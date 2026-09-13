from astrosphere.models.celestial_registry import CELESTIAL_OBJECT_LOOKUP
from astrosphere.models.planetary import PlanetaryObject


_SKYFIELD_NAMES = {
    "mercury": "mercury barycenter",
    "venus": "venus barycenter",
    "earth": "earth",
    "mars": "mars barycenter",
    "jupiter": "jupiter barycenter",
    "saturn": "saturn barycenter",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluto": "pluto barycenter",
}


PLANETS = [
    PlanetaryObject(
        CELESTIAL_OBJECT_LOOKUP[object_id].name,
        _SKYFIELD_NAMES[object_id],
    )
    for object_id in _SKYFIELD_NAMES
]


PLANET_LOOKUP = {
    planet.name.lower(): planet
    for planet in PLANETS
}
