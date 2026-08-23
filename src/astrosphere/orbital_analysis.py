from datetime import datetime

from astrosphere.astronomy.orbital_analysis import (
    analyze_earth_planet_distance,
)

from astrosphere.astronomy.planets import PLANET_LOOKUP
from astrosphere.reporting import print_orbital_report
from astrosphere.visualization import plot_distance


def main():
    print("ASTROSPHERE")
    print("Earth -> Planet Orbital Distance Analysis")
    print("=" * 70)

    print()
    print("Available planets:")
    print()

    for planet in PLANET_LOOKUP.values():
        if planet.name != "Earth":
            print(f"- {planet.name}")

    print()

    planet_name = input(
        "Enter planet name: "
    ).strip().lower()

    if planet_name not in PLANET_LOOKUP:
        print()
        print(f"Unknown planet: {planet_name}")
        return

    selected_planet = PLANET_LOOKUP[planet_name]

    if selected_planet.name == "Earth":
        print()
        print("Earth cannot be selected because")
        print("the analysis measures Earth -> Planet distance.")
        return

    print()
    print(
        f"Analyzing Earth -> "
        f"{selected_planet.name}..."
    )

    start_date = datetime(2026, 8, 22)

    results = analyze_earth_planet_distance(
        planet_name=selected_planet.skyfield_name,
        start_date=start_date,
        months=12,
        interval_days=1,
    )

    print_orbital_report(
        results,
        selected_planet.name,
    )

    print()
    print("Generating visualization...")

    plot_distance(
        results,
        selected_planet.name,
    )


if __name__ == "__main__":
    main()