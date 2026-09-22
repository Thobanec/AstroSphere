from datetime import datetime, timedelta, timezone

from astrosphere.astronomy.ephemeris import load_de440s
from astrosphere.astronomy.planets import PLANET_LOOKUP
from skyfield.api import load
from skyfield.framelib import ecliptic_frame


def calculate_planetary_trajectory(
    planet_name,
    observation_time=None,
    days=365,
    samples=181,
):
    """
    Calculate a time-based heliocentric trajectory for a planet.

    Positions are returned in heliocentric ecliptic coordinates,
    which are suitable for Solar System visualization.
    """

    if not isinstance(planet_name, str) or not planet_name.strip():
        raise ValueError("Planet name is required.")

    planet_name = planet_name.strip().lower()

    if planet_name not in PLANET_LOOKUP:
        raise ValueError(
            f"Unsupported planet: {planet_name}"
        )

    if days <= 0:
        raise ValueError("days must be greater than zero.")

    if samples < 2:
        raise ValueError("samples must be at least 2.")

    if observation_time is None:
        observation_time = datetime.now(timezone.utc)

    if observation_time.tzinfo is None:
        observation_time = observation_time.replace(
            tzinfo=timezone.utc
        )

    planets = load_de440s()
    timescale = load.timescale()

    planet = planets[PLANET_LOOKUP[planet_name].skyfield_name]
    sun = planets["sun"]

    start_time = observation_time
    end_time = observation_time + timedelta(days=days)

    interval_seconds = (
        (end_time - start_time).total_seconds()
        / (samples - 1)
    )

    datetimes = [
        start_time + timedelta(
            seconds=interval_seconds * index
        )
        for index in range(samples)
    ]

    skyfield_times = timescale.from_datetimes(datetimes)

    positions = (
        planet.at(skyfield_times)
        - sun.at(skyfield_times)
    )

    x, y, z = positions.frame_xyz(ecliptic_frame).au

    results = []

    for index, date_time in enumerate(datetimes):
        results.append(
            {
                "date": date_time,
                "x_au": float(x[index]),
                "y_au": float(y[index]),
                "z_au": float(z[index]),
            }
        )

    return results
