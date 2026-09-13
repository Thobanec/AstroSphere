from math import sqrt

from astrosphere.astronomy.asteroids import (
    AU_KM,
    SUN_GM_KM3_S2,
    create_asteroid_orbit_from_mpc,
    get_asteroid_orbit_data,
    _normalize_observation_time,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)
from astrosphere.models.scientific import (
    DataSource,
    Observation,
    Position,
    ScientificData,
    ScientificProvenance,
    Velocity,
)
from skyfield.api import load
from skyfield.framelib import ecliptic_frame


_MPC_SOURCE = DataSource(
    name="Minor Planet Center",
    provider="MPC",
    url="https://data.minorplanetcenter.net/",
    dataset="MPC Orbital Elements",
)


def get_asteroid_scientific_data(
    designation,
    observation_time=None,
):
    """
    Return asteroid data using the common ScientificData contract.
    """

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

    mpc_orbit = data[0]["mpc_orb"][0]
    coefficients = dict(
        zip(
            mpc_orbit["COM"]["coefficient_names"],
            mpc_orbit["COM"]["coefficient_values"],
        )
    )

    object_id = (
        f"asteroid:{mpc_orbit['designation_data']['permid']}"
    )

    obj = get_celestial_object(object_id)

    if obj is None:
        raise ValueError(
            "Asteroid is not registered as a "
            "canonical celestial object."
        )

    orbit = create_asteroid_orbit_from_mpc(
        data,
        timescale,
    )

    position, velocity = (
        orbit.at(time)
        .frame_xyz_and_velocity(
            ecliptic_frame
        )
    )

    q = float(coefficients["q"])
    e = float(coefficients["e"])

    semimajor_axis_au = (
        q / (1.0 - e)
    )

    semimajor_axis_km = (
        semimajor_axis_au * AU_KM
    )

    orbital_period_days = (
        2.0 * 3.141592653589793
        / sqrt(
            SUN_GM_KM3_S2
            / semimajor_axis_km**3
        )
        / 86400.0
    )

    return ScientificData(
        object_id=obj.id,
        observation=Observation(
            observation_time=(
                observation_time.isoformat()
            ),
            source=_MPC_SOURCE,
        ),
        position=Position(
            x=float(position.au[0]),
            y=float(position.au[1]),
            z=float(position.au[2]),
            unit="AU",
            frame="heliocentric_ecliptic",
        ),
        velocity=Velocity(
            x=float(velocity.au_per_d[0]),
            y=float(velocity.au_per_d[1]),
            z=float(velocity.au_per_d[2]),
            unit="AU/day",
            frame="heliocentric_ecliptic",
        ),
        orbital_properties={
            "perihelion_distance_au": q,
            "semimajor_axis_au": (
                semimajor_axis_au
            ),
            "eccentricity": e,
            "inclination_degrees": (
                float(coefficients["i"])
            ),
            "longitude_of_ascending_node_degrees": (
                float(coefficients["node"])
            ),
            "argument_of_perihelion_degrees": (
                float(coefficients["argperi"])
            ),
            "perihelion_time_mjd": (
                float(coefficients["peri_time"])
            ),
            "yarkovsky": (
                float(coefficients["yarkovski"])
            ),
            "epoch_mjd": (
                float(
                    mpc_orbit["epoch_data"]["epoch"]
                )
            ),
            "epoch_timesystem": (
                mpc_orbit["epoch_data"]["timesystem"]
            ),
            "orbital_period_days": (
                orbital_period_days
            ),
        },
        orbital_properties_source=_MPC_SOURCE,
        provenance=ScientificProvenance(
            sources=(_MPC_SOURCE,),
            reference_frames=(
                "heliocentric_ecliptic",
            ),
        ),
    )
