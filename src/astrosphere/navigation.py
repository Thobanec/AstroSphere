from astrosphere.models.celestial_registry import (
    get_celestial_object,
)


def get_celestial_object_url(object_id):
    obj = get_celestial_object(object_id)

    if obj is None:
        return None

    if obj.id == "solar-system":
        return "/solar-system"

    if obj.id == "sun":
        return "/solar-system"

    if obj.object_type in {"planet", "dwarf_planet"}:
        return f"/planet/{obj.name.lower()}"

    if obj.object_type == "asteroid":
        designation = obj.id.split(":", 1)[1]
        return f"/asteroid?designation={designation}"

    if obj.object_type == "spacecraft":
        norad_id = obj.id.split(":", 1)[1]
        return f"/spacecraft?norad_id={norad_id}"

    return f"/celestial/{obj.id}"
