import json
import math
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

import pandas as pd
from skyfield.api import load
from skyfield.data import mpc
from skyfield.framelib import ecliptic_frame
from skyfield.errors import EphemerisRangeError


class AsteroidNotFoundError(Exception):
    """Raised when the MPC cannot find the requested asteroid."""


class AsteroidDataError(Exception):
    """Raised when the MPC returns unusable asteroid data."""


class AsteroidServiceError(Exception):
    """Raised when the MPC service cannot be reached."""


MPC_ORBITS_URL = "https://data.minorplanetcenter.net/api/get-orb"

SUN_GM_KM3_S2 = 1.32712440018e11
AU_KM = 149597870.7


def get_asteroid_orbit_data(designation):
    """
    Retrieve orbital elements for an asteroid from the
    Minor Planet Center Orbits API.
    """

    payload = json.dumps(
        {
            "desig": designation,
        }
    ).encode("utf-8")

    request = Request(
        MPC_ORBITS_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=30,
        ) as response:
            data = json.load(response)

    except Exception as exc:
        raise AsteroidServiceError(
            "Unable to retrieve asteroid data "
            "from the Minor Planet Center."
        ) from exc

    if not isinstance(data, list) or not data:
        raise AsteroidNotFoundError(
            "Asteroid was not found."
        )

    if not isinstance(data[0], dict):
        raise AsteroidDataError(
            "Invalid asteroid data returned "
            "by the Minor Planet Center."
        )

    if not data[0].get("mpc_orb"):
        raise AsteroidNotFoundError(
            "Asteroid was not found."
        )

    return data


def create_asteroid_orbit_from_mpc(
    asteroid_data,
    timescale=None,
):
    """
    Create a Skyfield asteroid orbit directly from
    orbital elements returned by the MPC API.
    """

    if timescale is None:
        timescale = load.timescale()

    mpc_orbit = asteroid_data[0]["mpc_orb"][0]

    com = mpc_orbit["COM"]

    coefficients = dict(
        zip(
            com["coefficient_names"],
            com["coefficient_values"],
        )
    )

    q = coefficients["q"]
    e = coefficients["e"]

    semimajor_axis_au = q / (1.0 - e)

    epoch = mpc_orbit["epoch_data"]["epoch"]
    peri_time = coefficients["peri_time"]

    semimajor_axis_km = (
        semimajor_axis_au * AU_KM
    )

    mean_motion = (
        math.sqrt(
            SUN_GM_KM3_S2
            / semimajor_axis_km**3
        )
        * 86400.0
    )

    mean_anomaly = (
        mean_motion
        * (epoch - peri_time)
    )

    mean_anomaly_degrees = (
        math.degrees(mean_anomaly) % 360.0
    )

    julian_date = epoch + 2400000.5
    epoch_packed = f"K{int(julian_date):07d}"

    designation = (
        mpc_orbit["designation_data"]
        ["orbfit_name"]
    )

    row = pd.Series(
        {
            "semimajor_axis_au": semimajor_axis_au,
            "eccentricity": e,
            "inclination_degrees": (
                coefficients["i"]
            ),
            "longitude_of_ascending_node_degrees": (
                coefficients["node"]
            ),
            "argument_of_perihelion_degrees": (
                coefficients["argperi"]
            ),
            "mean_anomaly_degrees": (
                mean_anomaly_degrees
            ),
            "epoch_packed": epoch_packed,
            "designation": designation,
        }
    )

    return create_asteroid_orbit(
        row,
        timescale,
    )


def load_asteroid_data(url):
    """
    Load MPC asteroid orbital elements from a URL.
    """

    with load.open(url) as file:
        return mpc.load_mpcorb_dataframe(file)


def create_asteroid_orbit(
    asteroid_row,
    timescale=None,
):
    """
    Create a Skyfield asteroid orbit from an MPCORB
    dataframe row.
    """

    if timescale is None:
        timescale = load.timescale()

    return mpc.mpcorb_orbit(
        asteroid_row,
        timescale,
        SUN_GM_KM3_S2,
    )


def _normalize_observation_time(observation_time):
    if observation_time is None:
        return datetime.now(timezone.utc)

    if observation_time.tzinfo is None:
        return observation_time.replace(
            tzinfo=timezone.utc
        )

    return observation_time.astimezone(
        timezone.utc
    )


def track_asteroid(
    designation,
    observation_time=None,
):
    """
    Retrieve an asteroid's current orbital data from the
    MPC and calculate its heliocentric and Earth-relative
    position.

    Returns a dictionary containing the asteroid identity,
    observation time, position, distance from Earth, and
    relative velocity.
    """

    from astrosphere.astronomy.calculations import (
        calculate_distance_km,
        calculate_relative_velocity_km_s,
    )
    from astrosphere.astronomy.ephemeris import (
        load_de440s,
    )

    timescale = load.timescale()

    observation_time = _normalize_observation_time(
        observation_time
    )

    time = timescale.from_datetime(
        observation_time
    )

    data = get_asteroid_orbit_data(
        designation
    )

    orbit = create_asteroid_orbit_from_mpc(
        data,
        timescale,
    )

    ephemeris = load_de440s()

    earth = ephemeris["earth"]

    asteroid_position = orbit.at(time)

    earth_position = None
    distance_km = None
    relative_velocity_km_s = None
    earth_relative_data_available = True

    try:
        earth_position = earth.at(time)

        distance_km = calculate_distance_km(
            earth_position,
            asteroid_position,
        )

        relative_velocity_km_s = (
            calculate_relative_velocity_km_s(
                earth_position,
                asteroid_position,
            )
        )

    except EphemerisRangeError:
        earth_relative_data_available = False

    heliocentric_ecliptic = asteroid_position.frame_xyz(
            ecliptic_frame
        ).au

    mpc_orbit = data[0]["mpc_orb"][0]

    designation_data = mpc_orbit[
        "designation_data"
    ]

    return {
        "designation": designation_data[
            "iau_designation"
        ],
        "name": designation_data["name"],
        "permanent_designation": designation_data[
            "permid"
        ],
        "observation_time": (
            observation_time.isoformat()
        ),
        "distance_from_earth_km": distance_km,
        "relative_velocity_km_s": (
            relative_velocity_km_s
        ),
        "earth_relative_data_available": (
            earth_relative_data_available
        ),
        "heliocentric_position_au": {
            "x": float(
                asteroid_position.position.au[0]
            ),
            "y": float(
                asteroid_position.position.au[1]
            ),
            "z": float(
                asteroid_position.position.au[2]
            ),
        },
        "heliocentric_ecliptic_position_au": {
            "x": float(
                heliocentric_ecliptic[0]
            ),
            "y": float(
                heliocentric_ecliptic[1]
            ),
            "z": float(
                heliocentric_ecliptic[2]
            ),
        },
    }


def calculate_asteroid_trajectory(
    designation,
    observation_time=None,
    samples=181,
):
    """
    Calculate one full orbital-period trajectory for an asteroid.

    Positions are returned in heliocentric ecliptic coordinates,
    which are appropriate for a Solar System map because the major
    planetary orbits lie close to the ecliptic plane.
    """

    timescale = load.timescale()

    observation_time = _normalize_observation_time(
        observation_time
    )

    data = get_asteroid_orbit_data(
        designation
    )

    orbit = create_asteroid_orbit_from_mpc(
        data,
        timescale,
    )

    mpc_orbit = data[0]["mpc_orb"][0]

    com = mpc_orbit["COM"]

    coefficients = dict(
        zip(
            com["coefficient_names"],
            com["coefficient_values"],
        )
    )

    q = coefficients["q"]
    e = coefficients["e"]

    semimajor_axis_au = (
        q / (1.0 - e)
    )

    semimajor_axis_km = (
        semimajor_axis_au * AU_KM
    )

    orbital_period_days = (
        2.0 * math.pi
        / math.sqrt(
            SUN_GM_KM3_S2
            / semimajor_axis_km**3
        )
        / 86400.0
    )

    sample_count = max(
        61,
        min(
            int(samples),
            361,
        ),
    )

    # Provide a long simulation window around the requested date.
    #
    # Five years on either side gives the browser enough
    # trajectory coverage for smooth high-speed simulation.
    trajectory_half_span_days = (
        365.25 * 5.0
    )

    datetimes = [
        observation_time
        + timedelta(
            days=(
                -trajectory_half_span_days
                + (
                    (trajectory_half_span_days * 2.0)
                    * index
                    / (sample_count - 1)
                )
            )
        )
        for index in range(
            sample_count
        )
    ]

    skyfield_times = (
        timescale.from_datetimes(
            datetimes
        )
    )

    positions = orbit.at(
            skyfield_times
        ).frame_xyz(
            ecliptic_frame
        ).au

    points = []

    for index, point_time in enumerate(
        datetimes
    ):

        points.append(
            {
                "observation_time": (
                    point_time.isoformat()
                ),
                "x": float(
                    positions[0][index]
                ),
                "y": float(
                    positions[1][index]
                ),
                "z": float(
                    positions[2][index]
                ),
            }
        )

    designation_data = mpc_orbit[
        "designation_data"
    ]

    return {
        "designation": designation_data[
            "iau_designation"
        ],
        "name": designation_data["name"],
        "permanent_designation": designation_data[
            "permid"
        ],
        "observation_time": (
            observation_time.isoformat()
        ),
        "orbital_period_days": (
            orbital_period_days
        ),
        "samples": sample_count,
        "coordinate_frame": (
            "heliocentric_ecliptic"
        ),
        "points": points,
    }
