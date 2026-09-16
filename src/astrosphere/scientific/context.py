from astrosphere.models.celestial_registry import (
    get_ancestors,
    get_celestial_object,
    get_children,
    get_parent_object,
)
from astrosphere.scientific.service import (
    get_scientific_data,
)


def get_celestial_object_context(
    object_id,
    observation_time=None,
):
    obj = get_celestial_object(object_id)

    if obj is None:
        raise ValueError(
            f"Unknown celestial object: {object_id}"
        )

    scientific_data = None

    if obj.object_type in {
        "planet",
        "dwarf_planet",
        "asteroid",
        "spacecraft",
    }:
        scientific_data = get_scientific_data(
            obj.id,
            observation_time=observation_time,
        )

    parent = get_parent_object(obj.id)

    system = (
        get_celestial_object(obj.system_id)
        if obj.system_id
        else None
    )

    return {
        "object": obj,
        "parent": parent,
        "system": system,
        "ancestors": get_ancestors(obj.id),
        "children": get_children(obj.id),
        "scientific_data": scientific_data,
    }
