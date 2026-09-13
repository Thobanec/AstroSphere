from astrosphere.models.celestial_registry import (
    get_ancestors,
    get_celestial_object,
    get_children,
)
from astrosphere.scientific.service import (
    get_scientific_data,
)


EARTH_OBJECT_ID = "earth"


def get_earth_context(observation_time=None):
    """
    Return the canonical and scientific context for Earth.
    """

    earth = get_celestial_object(
        EARTH_OBJECT_ID
    )

    if earth is None:
        raise ValueError(
            "Earth is not registered as a canonical celestial object."
        )

    scientific_data = get_scientific_data(
        EARTH_OBJECT_ID,
        observation_time=observation_time,
    )

    ancestors = get_ancestors(
        EARTH_OBJECT_ID
    )

    children = get_children(
        EARTH_OBJECT_ID
    )

    return {
        "object": earth,
        "scientific_data": scientific_data,
        "ancestors": ancestors,
        "children": children,
    }
