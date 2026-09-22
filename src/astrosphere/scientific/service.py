from datetime import datetime, timezone

from skyfield.api import load

from astrosphere.astronomy.ephemeris import load_de440s
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)
from astrosphere.models.planetary_scientific_catalog import (
    get_planetary_scientific_properties,
)
from astrosphere.models.stellar_scientific_catalog import (
    get_stellar_scientific_properties,
)
from astrosphere.models.scientific import (
    DataSource,
    Observation,
    Position,
    ScientificData,
    ScientificProvenance,
    Velocity,
)

from astrosphere.scientific.asteroids import (
    get_asteroid_scientific_data,
)
from astrosphere.scientific.spacecraft import (
    get_spacecraft_scientific_data,
)


_DE440S_SOURCE = DataSource(
    name="JPL DE440S",
    provider="NASA/JPL",
    dataset="DE440S",
)


def get_ephemeris_data_source():
    """
    Return the data source metadata for the planetary ephemeris.
    """
    return _DE440S_SOURCE


_SKYFIELD_NAMES = {
    "mercury": "mercury barycenter",
    "venus": "venus barycenter",
    "earth": "earth",
    "mars": "mars barycenter",
    "jupiter": "jupiter barycenter",
    "saturn": "saturn barycenter",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluto": "pluto barycenter",
}


def get_scientific_data(
    object_id,
    observation_time=None,
):
    """
    Return scientific data for a canonical celestial object.

    Currently supports Solar System planetary bodies
    represented by the DE440S ephemeris.
    """

    obj = get_celestial_object(object_id)

    if obj is None:
        raise ValueError(
            f"Unknown celestial object: {object_id}"
        )

    if obj.object_type == "star":
        stellar_properties = (
            get_stellar_scientific_properties(
                obj.id
            )
        )

        if stellar_properties is None:
            raise ValueError(
                f"Scientific data is not yet supported "
                f"for: {obj.id}"
            )

        return ScientificData(
            object_id=obj.id,
            observation=None,
            position=None,
            velocity=None,
            physical_properties=(
                stellar_properties.physical_properties
            ),
            orbital_properties=None,
            physical_properties_source=(
                stellar_properties.source
            ),
            orbital_properties_source=None,
            stellar_properties=(
                stellar_properties.stellar_properties
            ),
            stellar_properties_source=(
                stellar_properties.source
            ),
            provenance=ScientificProvenance(
                sources=(
                    stellar_properties.source,
                ),
                reference_frames=(),
            ),
        )

    if obj.object_type == "asteroid":
        designation = obj.id.split(
            ":", 1
        )[1]
        return get_asteroid_scientific_data(
            designation,
            observation_time=observation_time,
        )

    if obj.object_type == "spacecraft":
        norad_id = obj.id.split(
            ":", 1
        )[1]
        return get_spacecraft_scientific_data(
            norad_id,
            observation_time=observation_time,
        )

    if obj.id not in _SKYFIELD_NAMES:
        raise ValueError(
            f"Scientific data is not yet supported "
            f"for: {obj.id}"
        )

    if observation_time is None:
        observation_time = datetime.now(
            timezone.utc
        )
    elif not isinstance(
        observation_time,
        datetime,
    ):
        observation_time = observation_time.utc_datetime()

    if observation_time.tzinfo is None:
        observation_time = observation_time.replace(
            tzinfo=timezone.utc
        )
    else:
        observation_time = observation_time.astimezone(
            timezone.utc
        )

    timescale = load.timescale()

    time = timescale.from_datetime(
        observation_time
    )

    ephemeris = load_de440s()

    body = ephemeris[
        _SKYFIELD_NAMES[obj.id]
    ]

    position = body.at(time)

    position_au = position.position.au
    velocity_au_per_day = position.velocity.au_per_d

    planetary_properties = (
        get_planetary_scientific_properties(
            obj.id
        )
    )

    physical_properties = None
    orbital_properties = None

    if planetary_properties is not None:
        physical_properties = (
            planetary_properties.physical_properties
        )
        orbital_properties = (
            planetary_properties.orbital_properties
        )

    return ScientificData(
        object_id=obj.id,
        observation=Observation(
            observation_time=(
                observation_time.isoformat()
            ),
            source=_DE440S_SOURCE,
        ),
        position=Position(
            x=float(position_au[0]),
            y=float(position_au[1]),
            z=float(position_au[2]),
            unit="AU",
            frame="ICRF",
        ),
        velocity=Velocity(
            x=float(velocity_au_per_day[0]),
            y=float(velocity_au_per_day[1]),
            z=float(velocity_au_per_day[2]),
            unit="AU/day",
            frame="ICRF",
        ),
        physical_properties=physical_properties,
        orbital_properties=orbital_properties,
        physical_properties_source=(
            planetary_properties.source
            if planetary_properties
            else None
        ),
        orbital_properties_source=(
            planetary_properties.source
            if planetary_properties
            else None
        ),
        provenance=ScientificProvenance(
            sources=tuple(
                source
                for source in (
                    _DE440S_SOURCE,
                    (
                        planetary_properties.source
                        if planetary_properties
                        else None
                    ),
                )
                if source is not None
            ),
            reference_frames=("ICRF",),
        ),
    )
