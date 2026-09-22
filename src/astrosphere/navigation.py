from astrosphere.models.celestial_registry import (
    get_celestial_object,
)


def get_celestial_object_url(object_id):
    """
    Return the canonical web URL for a registered celestial object.

    Dedicated explorer pages are used for major navigational contexts.
    All other registered celestial objects use the generic canonical
    celestial-object explorer route.
    """
    if not isinstance(object_id, str) or not object_id.strip():
        return None

    normalized_object_id = object_id.strip().lower()
    obj = get_celestial_object(normalized_object_id)

    if obj is None:
        return None

    if obj.id == "milky-way":
        return "/galaxy"

    if obj.id == "solar-system":
        return "/solar-system"

    return f"/celestial/{obj.id}"
