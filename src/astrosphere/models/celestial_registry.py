from astrosphere.models.celestial import CelestialObject


SOLAR_SYSTEM_ID = "solar-system"


CELESTIAL_OBJECTS = [
    CelestialObject(
        id="solar-system",
        name="Solar System",
        object_type="system",
        description="The planetary system centered on the Sun.",
    ),
    CelestialObject(
        id="sun",
        name="Sun",
        object_type="star",
        parent_id="solar-system",
        system_id="solar-system",
    ),
    CelestialObject(
        id="mercury",
        name="Mercury",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="venus",
        name="Venus",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="earth",
        name="Earth",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="mars",
        name="Mars",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="jupiter",
        name="Jupiter",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="saturn",
        name="Saturn",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="uranus",
        name="Uranus",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="neptune",
        name="Neptune",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="pluto",
        name="Pluto",
        object_type="dwarf_planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="asteroid:99942",
        name="Apophis",
        object_type="asteroid",
        parent_id="solar-system",
        system_id="solar-system",
        description="Near-Earth asteroid 99942 Apophis.",
    ),
    CelestialObject(
        id="spacecraft:25544",
        name="ISS",
        object_type="spacecraft",
        parent_id="earth",
        system_id="solar-system",
        description="International Space Station.",
    ),
]


CELESTIAL_OBJECT_LOOKUP = {
    obj.id: obj for obj in CELESTIAL_OBJECTS
}

def get_celestial_object(object_id):
    return CELESTIAL_OBJECT_LOOKUP.get(
        object_id.strip().lower()
    )


def get_parent_object(object_id):
    obj = get_celestial_object(object_id)

    if obj is None or obj.parent_id is None:
        return None

    return get_celestial_object(obj.parent_id)


def get_ancestors(object_id):
    ancestors = []
    current = get_celestial_object(object_id)

    while current is not None and current.parent_id is not None:
        parent = get_celestial_object(current.parent_id)

        if parent is None:
            break

        ancestors.append(parent)
        current = parent

    return ancestors


def get_children(object_id):
    object_id = object_id.strip().lower()

    return [
        obj
        for obj in CELESTIAL_OBJECTS
        if obj.parent_id == object_id
    ]
