from calendar import monthrange
from datetime import timedelta

from skyfield.api import load

from astrosphere.astronomy.calculations import (
    calculate_distance_km,
    calculate_relative_velocity_km_s,
)


def add_months(date, months):
    """
    Add calendar months to a datetime.

    If the target month does not contain the original day,
    the last valid day of the target month is used.
    """

    total_months = (
        date.year * 12
        + (date.month - 1)
        + months
    )

    year = total_months // 12
    month = total_months % 12 + 1

    last_day = monthrange(year, month)[1]

    day = min(date.day, last_day)

    return date.replace(
        year=year,
        month=month,
        day=day,
    )


def analyze_body_distance(
    reference_body_name,
    target_body_name,
    start_date,
    months=12,
    interval_days=30,
):
    """
    Calculate distance and relative velocity between two
    Solar System bodies at regular intervals.

    The analysis period uses calendar months rather than
    assuming every month contains exactly 30 days.
    """

    if months <= 0:
        raise ValueError(
            "months must be greater than zero."
        )

    if interval_days <= 0:
        raise ValueError(
            "interval_days must be greater than zero."
        )

    if reference_body_name == target_body_name:
        raise ValueError(
            "Reference body and target body "
            "cannot be the same."
        )

    planets = load("de440s.bsp")
    timescale = load.timescale()

    reference_body = planets[reference_body_name]
    target_body = planets[target_body_name]

    end_date = add_months(
        start_date,
        months,
    )

    results = []

    current_date = start_date

    while current_date <= end_date:

        time = timescale.utc(
            current_date.year,
            current_date.month,
            current_date.day,
        )

        reference_position = reference_body.at(time)
        target_position = target_body.at(time)

        distance_km = calculate_distance_km(
            reference_position,
            target_position,
        )

        relative_velocity_km_s = (
            calculate_relative_velocity_km_s(
                reference_position,
                target_position,
            )
        )

        results.append(
            {
                "date": current_date,
                "distance_km": distance_km,
                "relative_velocity_km_s": (
                    relative_velocity_km_s
                ),
            }
        )

        current_date += timedelta(
            days=interval_days
        )

    # Include the exact end date when the selected
    # interval does not land exactly on it.
    if results[-1]["date"] != end_date:

        time = timescale.utc(
            end_date.year,
            end_date.month,
            end_date.day,
        )

        reference_position = reference_body.at(time)
        target_position = target_body.at(time)

        distance_km = calculate_distance_km(
            reference_position,
            target_position,
        )

        relative_velocity_km_s = (
            calculate_relative_velocity_km_s(
                reference_position,
                target_position,
            )
        )

        results.append(
            {
                "date": end_date,
                "distance_km": distance_km,
                "relative_velocity_km_s": (
                    relative_velocity_km_s
                ),
            }
        )

    return results


def analyze_earth_planet_distance(
    planet_name,
    start_date,
    months=12,
    interval_days=30,
):
    """
    Compatibility wrapper for Earth-to-planet analysis.
    """

    return analyze_body_distance(
        reference_body_name="earth",
        target_body_name=planet_name,
        start_date=start_date,
        months=months,
        interval_days=interval_days,
    )