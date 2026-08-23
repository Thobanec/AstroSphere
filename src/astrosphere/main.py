from astrosphere.astronomy.calculations import (
    calculate_distance_km,
    get_current_time,
    load_solar_system,
)

from astrosphere.astronomy.planets import PLANETS


def main():
    print("🌌 AstroSphere")
    print("Solar System Data Engine")
    print("=" * 80)

    print()
    print("Loading astronomical data...")

    solar_system = load_solar_system()
    now = get_current_time()

    sun = solar_system["sun"]
    earth = solar_system["earth"]

    sun_position = sun.at(now)
    earth_position = earth.at(now)

    print()
    print("Current Solar System Information")
    print("-" * 80)
    print(f"Date: {now.utc_strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()

    print(
        f"{'OBJECT':<12}"
        f"{'FROM SUN (KM)':>22}"
        f"{'FROM EARTH (KM)':>22}"
    )

    print("-" * 80)

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

        print(
            f"{planet.name:<12}"
            f"{distance_from_sun:>22,.0f}"
            f"{distance_from_earth:>22,.0f}"
        )

    print()
    print(f"Tracked Solar System objects: {len(PLANETS)}")


if __name__ == "__main__":
    main()