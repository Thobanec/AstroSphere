from astrosphere.astronomy.calculations import (
    calculate_distance_km,
    get_current_time,
    load_solar_system,
)

from astrosphere.astronomy.planets import PLANETS


def generate_solar_system_overview():
    solar_system = load_solar_system()
    now = get_current_time()

    sun = solar_system["sun"]
    earth = solar_system["earth"]

    sun_position = sun.at(now)
    earth_position = earth.at(now)

    results = []

    for planet in PLANETS:
        body = solar_system[planet.skyfield_name]
        body_position = body.at(now)

        distance_from_sun = calculate_distance_km(
            body_position,
            sun_position,
        )

        distance_from_earth = calculate_distance_km(
            body_position,
            earth_position,
        )

        results.append(
            {
                "name": planet.name,
                "distance_from_sun": distance_from_sun,
                "distance_from_earth": distance_from_earth,
            }
        )

    return now, results