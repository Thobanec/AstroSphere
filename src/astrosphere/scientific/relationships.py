from astrosphere.models.celestial_registry import (
    get_ancestors,
    get_celestial_object,
    get_children,
    get_parent_object,
)


def get_celestial_object_relationships(object_id):
    obj = get_celestial_object(object_id)

    if obj is None:
        raise ValueError(
            f"Unknown celestial object: {object_id}"
        )

    return {
        "object": obj,
        "parent": get_parent_object(object_id),
        "ancestors": get_ancestors(object_id),
        "children": get_children(object_id),
    }
