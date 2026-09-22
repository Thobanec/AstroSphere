from astrosphere.models.celestial import CelestialObject


SOLAR_SYSTEM_ID = "solar-system"


CELESTIAL_OBJECTS = [
    CelestialObject(
        id="universe",
        name="Universe",
        object_type="universe",
        description="The observable universe containing galaxies and their systems.",
    ),
    CelestialObject(
        id="milky-way",
        name="Milky Way",
        object_type="galaxy",
        parent_id="universe",
        description="The galaxy containing the Solar System.",
    ),
    CelestialObject(
        id="solar-system",
        name="Solar System",
        object_type="system",
        parent_id="milky-way",
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
        id="sirius",
        name="Sirius",
        object_type="star",
        parent_id="milky-way",
        description="Bright star system in the Milky Way.",
    ),
    CelestialObject(
        id="proxima-centauri",
        name="Proxima Centauri",
        object_type="star",
        parent_id="milky-way",
        description="Nearest known stellar neighbor to the Solar System.",
    ),
    CelestialObject(
        id="betelgeuse",
        name="Betelgeuse",
        object_type="star",
        parent_id="milky-way",
        description="Red supergiant star in the Milky Way.",
    ),
    CelestialObject(
        id="vega",
        name="Vega",
        object_type="star",
        parent_id="milky-way",
        description="Bright star in the constellation Lyra.",
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
        id="moon",
        name="Moon",
        object_type="moon",
        parent_id="earth",
        system_id="solar-system",
        description="Earth's natural satellite.",
    ),
    CelestialObject(
        id="mars",
        name="Mars",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="phobos",
        name="Phobos",
        object_type="moon",
        parent_id="mars",
        system_id="solar-system",
        description="Natural satellite of Mars.",
    ),
    CelestialObject(
        id="deimos",
        name="Deimos",
        object_type="moon",
        parent_id="mars",
        system_id="solar-system",
        description="Natural satellite of Mars.",
    ),
    CelestialObject(
        id="jupiter",
        name="Jupiter",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="io",
        name="Io",
        object_type="moon",
        parent_id="jupiter",
        system_id="solar-system",
        description="Natural satellite of Jupiter.",
    ),
    CelestialObject(
        id="europa",
        name="Europa",
        object_type="moon",
        parent_id="jupiter",
        system_id="solar-system",
        description="Natural satellite of Jupiter.",
    ),
    CelestialObject(
        id="ganymede",
        name="Ganymede",
        object_type="moon",
        parent_id="jupiter",
        system_id="solar-system",
        description="Natural satellite of Jupiter.",
    ),
    CelestialObject(
        id="callisto",
        name="Callisto",
        object_type="moon",
        parent_id="jupiter",
        system_id="solar-system",
        description="Natural satellite of Jupiter.",
    ),
    CelestialObject(
        id="saturn",
        name="Saturn",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="titan",
        name="Titan",
        object_type="moon",
        parent_id="saturn",
        system_id="solar-system",
        description="Natural satellite of Saturn.",
    ),
    CelestialObject(
        id="enceladus",
        name="Enceladus",
        object_type="moon",
        parent_id="saturn",
        system_id="solar-system",
        description="Natural satellite of Saturn.",
    ),
    CelestialObject(
        id="uranus",
        name="Uranus",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="miranda",
        name="Miranda",
        object_type="moon",
        parent_id="uranus",
        system_id="solar-system",
        description="Natural satellite of Uranus.",
    ),
    CelestialObject(
        id="titania",
        name="Titania",
        object_type="moon",
        parent_id="uranus",
        system_id="solar-system",
        description="Natural satellite of Uranus.",
    ),
    CelestialObject(
        id="oberon",
        name="Oberon",
        object_type="moon",
        parent_id="uranus",
        system_id="solar-system",
        description="Natural satellite of Uranus.",
    ),
    CelestialObject(
        id="neptune",
        name="Neptune",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="triton",
        name="Triton",
        object_type="moon",
        parent_id="neptune",
        system_id="solar-system",
        description="Natural satellite of Neptune.",
    ),
    CelestialObject(
        id="pluto",
        name="Pluto",
        object_type="dwarf_planet",
        parent_id="sun",
        system_id="solar-system",
    ),
    CelestialObject(
        id="charon",
        name="Charon",
        object_type="moon",
        parent_id="pluto",
        system_id="solar-system",
        description="Natural satellite of Pluto.",
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
