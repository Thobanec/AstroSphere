from astrosphere.models.planetary import PlanetaryObject


PLANETS = [
    PlanetaryObject("Mercury", "mercury barycenter"),
    PlanetaryObject("Venus", "venus barycenter"),
    PlanetaryObject("Earth", "earth"),
    PlanetaryObject("Mars", "mars barycenter"),
    PlanetaryObject("Jupiter", "jupiter barycenter"),
    PlanetaryObject("Saturn", "saturn barycenter"),
    PlanetaryObject("Uranus", "uranus barycenter"),
    PlanetaryObject("Neptune", "neptune barycenter"),
    PlanetaryObject("Pluto", "pluto barycenter"),
]

PLANET_LOOKUP = {
    planet.name.lower(): planet
    for planet in PLANETS
}