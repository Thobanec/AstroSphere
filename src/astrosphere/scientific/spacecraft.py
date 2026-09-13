from astrosphere.astronomy.spacecraft import (
    _get_spacecraft_tle_with_source,
    track_spacecraft,
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


def get_spacecraft_scientific_data(
    norad_id,
    observation_time=None,
):
    """
    Return spacecraft tracking data using the
    common ScientificData contract.
    """

    norad_id = str(norad_id).strip()

    if not norad_id.isdigit():
        raise ValueError(
            "NORAD ID must be numeric."
        )

    object_id = f"spacecraft:{norad_id}"

    obj = get_celestial_object(object_id)

    if obj is None:
        raise ValueError(
            "Spacecraft is not registered as a "
            "canonical celestial object."
        )

    tle, source_metadata = (
        _get_spacecraft_tle_with_source(
            norad_id
        )
    )

    tracking = track_spacecraft(
        tle["name"],
        tle["line1"],
        tle["line2"],
        observation_time=observation_time,
    )

    source = DataSource(
        name=source_metadata["provider"],
        provider=source_metadata["provider"],
        url=(
            "https://db.satnogs.org/"
            if source_metadata["provider"]
            == "SatNOGS DB"
            else "https://celestrak.org/"
        ),
        dataset=source_metadata["dataset"],
        upstream_source=source_metadata.get("upstream_source"),
    )

    return ScientificData(
        object_id=obj.id,
        observation=Observation(
            observation_time=tracking[
                "observation_time"
            ],
            source=source,
        ),
        position=Position(
            x=tracking["position_km"]["x"],
            y=tracking["position_km"]["y"],
            z=tracking["position_km"]["z"],
            unit="km",
            frame="geocentric",
        ),
        velocity=Velocity(
            x=tracking["velocity_km_s"]["x"],
            y=tracking["velocity_km_s"]["y"],
            z=tracking["velocity_km_s"]["z"],
            unit="km/s",
            frame="geocentric",
        ),
        provenance=ScientificProvenance(
            sources=(source,),
            reference_frames=("geocentric",),
        ),
    )
