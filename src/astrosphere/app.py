from astrosphere.analysis_config import AnalysisConfig

from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)

from astrosphere.cli import (
    select_analysis_date,
    select_analysis_interval,
    select_analysis_period,
    select_planet,
    select_reference_body,
    show_main_menu,
)

from astrosphere.overview import generate_solar_system_overview
from astrosphere.overview_report import print_solar_system_overview

from astrosphere.reporting import print_orbital_report
from astrosphere.visualization import plot_distance


def analyze_selected_planet():
    planet = select_planet()

    if planet is None:
        return

    reference_body = select_reference_body(planet)

    if reference_body is None:
        return

    analysis_date = select_analysis_date()

    if analysis_date is None:
        return

    months = select_analysis_period()

    if months is None:
        return

    interval_days = select_analysis_interval()

    if interval_days is None:
        return

    config = AnalysisConfig(
        start_date=analysis_date,
        months=months,
        interval_days=interval_days,
        reference_body=reference_body,
    )

    print()
    print(
        f"Analyzing "
        f"{config.reference_body.name} "
        f"-> {planet.name}..."
    )

    print(
        f"Analysis period: "
        f"{config.months} months"
    )

    print(
        f"Interval: every "
        f"{config.interval_days} day(s)"
    )

    print("Please wait...")

    results = analyze_body_distance(
        reference_body_name=(
            config.reference_body.skyfield_name
        ),
        target_body_name=planet.skyfield_name,
        start_date=config.start_date,
        months=config.months,
        interval_days=config.interval_days,
    )

    print_orbital_report(
        results,
        planet.name,
        reference_body=config.reference_body.name,
        interval_days=config.interval_days,
    )

    print()
    print("Generating visualization...")

    plot_distance(
        results,
        planet.name,
        reference_body=config.reference_body.name,
    )


def main():
    while True:
        show_main_menu()

        selection = input(
            "Select an option: "
        ).strip()

        if selection == "1":
            analyze_selected_planet()

        elif selection == "2":
            now, results = (
                generate_solar_system_overview()
            )

            print_solar_system_overview(
                now,
                results,
            )

            input(
                "Press Enter to return "
                "to the main menu..."
            )

        elif selection == "3":
            print()
            print(
                "Thank you for using AstroSphere."
            )
            print()
            break

        else:
            print()
            print(
                "Invalid selection. "
                "Please try again."
            )


if __name__ == "__main__":
    main()