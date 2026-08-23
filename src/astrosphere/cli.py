from datetime import datetime, timezone

from astrosphere.astronomy.planets import PLANETS


def get_available_planets():
    return [
        planet
        for planet in PLANETS
        if planet.name != "Earth"
    ]


def show_main_menu():
    print()
    print("=" * 60)
    print("                     ASTROSPHERE")
    print("              Solar System Analysis")
    print("=" * 60)

    print()
    print("1. Analyze a planet")
    print("2. Solar System overview")
    print("3. Exit")
    print()


def show_planet_menu():
    available_planets = get_available_planets()

    print()
    print("=" * 60)
    print("                 AVAILABLE PLANETS")
    print("=" * 60)

    for index, planet in enumerate(
        available_planets,
        start=1,
    ):
        print(f"{index}. {planet.name}")

    print()


def list_tracked_objects():
    show_planet_menu()

    input(
        "Press Enter to return to the main menu..."
    )


def select_planet():
    available_planets = get_available_planets()

    show_planet_menu()

    selection = input(
        "Select planet: "
    ).strip()

    if not selection.isdigit():
        print()
        print("Please enter a number.")
        return None

    index = int(selection) - 1

    if index < 0 or index >= len(available_planets):
        print()
        print("Invalid planet selection.")
        return None

    return available_planets[index]

def select_analysis_period():
    print()
    print("=" * 60)
    print("                 ANALYSIS PERIOD")
    print("=" * 60)

    print()
    print("1. 3 months")
    print("2. 6 months")
    print("3. 12 months")
    print()

    selection = input(
        "Select period: "
    ).strip()

    periods = {
        "1": 3,
        "2": 6,
        "3": 12,
    }

    if selection not in periods:
        print()
        print("Invalid period selection.")
        return None

    return periods[selection]

def select_analysis_date():
    print()
    print("=" * 60)
    print("                 ANALYSIS DATE")
    print("=" * 60)

    print()
    print("1. Start from today")
    print("2. Enter a historical date")
    print()

    selection = input(
        "Select option: "
    ).strip()

    if selection == "1":
        return datetime.now(timezone.utc)

    if selection == "2":
        date_text = input(
            "Enter date (YYYY-MM-DD): "
        ).strip()

        try:
            return datetime.strptime(
                date_text,
                "%Y-%m-%d",
            ).replace(tzinfo=timezone.utc)

        except ValueError:
            print()
            print(
                "Invalid date format. "
                "Please use YYYY-MM-DD."
            )
            return None

    print()
    print("Invalid date selection.")
    return None

def select_analysis_interval():
    print()
    print("=" * 60)
    print("              ANALYSIS INTERVAL")
    print("=" * 60)

    print()
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    print()

    selection = input(
        "Select interval: "
    ).strip()

    intervals = {
        "1": 1,
        "2": 7,
        "3": 30,
    }

    if selection not in intervals:
        print()
        print("Invalid interval selection.")
        return None

    return intervals[selection]

def select_reference_body(target_planet=None):
    available_bodies = [
        planet
        for planet in PLANETS
        if target_planet is None
        or planet.name != target_planet.name
    ]

    print()
    print("=" * 60)
    print("                 REFERENCE BODY")
    print("=" * 60)

    print()

    for index, planet in enumerate(available_bodies, start=1):
        print(f"{index}. {planet.name}")

    print()

    selection = input(
        "Select reference body: "
    ).strip()

    try:
        index = int(selection)
    except ValueError:
        print()
        print("Invalid reference body selection.")
        return None

    if index < 1 or index > len(available_bodies):
        print()
        print("Invalid reference body selection.")
        return None

    return available_bodies[index - 1]