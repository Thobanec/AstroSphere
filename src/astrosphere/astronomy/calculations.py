from datetime import datetime, timezone
from math import sqrt

from skyfield.api import load


def load_solar_system():
    """
    Load the DE440S Solar System ephemeris.
    """

    return load("de440s.bsp")


def get_current_time():
    """
    Return the current UTC time as a Skyfield Time object.
    """

    timescale = load.timescale()

    current_datetime = datetime.now(
        timezone.utc
    )

    return timescale.from_datetime(
        current_datetime
    )


def calculate_distance_km(
    reference_position,
    target_position,
):
    """
    Calculate the distance between two astronomical
    positions in kilometres.
    """

    reference_coordinates = (
        reference_position.position.km
    )

    target_coordinates = (
        target_position.position.km
    )

    dx = (
        target_coordinates[0]
        - reference_coordinates[0]
    )

    dy = (
        target_coordinates[1]
        - reference_coordinates[1]
    )

    dz = (
        target_coordinates[2]
        - reference_coordinates[2]
    )

    distance_km = sqrt(
        dx ** 2
        + dy ** 2
        + dz ** 2
    )

    return distance_km


def calculate_relative_velocity_km_s(
    reference_position,
    target_position,
):
    """
    Calculate the relative velocity between two
    astronomical bodies in kilometres per second.
    """

    reference_velocity = (
        reference_position.velocity.km_per_s
    )

    target_velocity = (
        target_position.velocity.km_per_s
    )

    dvx = (
        target_velocity[0]
        - reference_velocity[0]
    )

    dvy = (
        target_velocity[1]
        - reference_velocity[1]
    )

    dvz = (
        target_velocity[2]
        - reference_velocity[2]
    )

    relative_velocity_km_s = sqrt(
        dvx ** 2
        + dvy ** 2
        + dvz ** 2
    )

    return relative_velocity_km_s