from astrosphere.models.celestial_registry import (
    get_ancestors,
    get_celestial_object,
    get_children,
    get_parent_object,
)


def test_major_moons_are_registered():
    expected_moons = {
        "moon",
        "phobos",
        "deimos",
        "io",
        "europa",
        "ganymede",
        "callisto",
        "titan",
        "enceladus",
        "miranda",
        "titania",
        "oberon",
        "triton",
        "charon",
    }

    actual_moons = {
        object_id
        for object_id in (
            "moon",
            "phobos",
            "deimos",
            "io",
            "europa",
            "ganymede",
            "callisto",
            "titan",
            "enceladus",
            "miranda",
            "titania",
            "oberon",
            "triton",
            "charon",
        )
        if get_celestial_object(object_id) is not None
    }

    assert actual_moons == expected_moons


def test_major_moons_have_moon_object_type():
    moon_ids = (
        "moon",
        "phobos",
        "deimos",
        "io",
        "europa",
        "ganymede",
        "callisto",
        "titan",
        "enceladus",
        "miranda",
        "titania",
        "oberon",
        "triton",
        "charon",
    )

    for moon_id in moon_ids:
        moon = get_celestial_object(moon_id)

        assert moon is not None
        assert moon.object_type == "moon"


def test_moon_parent_relationships():
    expected_parents = {
        "moon": "earth",
        "phobos": "mars",
        "deimos": "mars",
        "io": "jupiter",
        "europa": "jupiter",
        "ganymede": "jupiter",
        "callisto": "jupiter",
        "titan": "saturn",
        "enceladus": "saturn",
        "miranda": "uranus",
        "titania": "uranus",
        "oberon": "uranus",
        "triton": "neptune",
        "charon": "pluto",
    }

    for moon_id, expected_parent_id in expected_parents.items():
        parent = get_parent_object(moon_id)

        assert parent is not None
        assert parent.id == expected_parent_id


def test_earth_children_include_moon():
    children = get_children("earth")

    child_ids = {
        child.id
        for child in children
    }

    assert "moon" in child_ids


def test_mars_children_include_phobos_and_deimos():
    children = get_children("mars")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "phobos",
        "deimos",
    }


def test_jupiter_children_include_major_moons():
    children = get_children("jupiter")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "io",
        "europa",
        "ganymede",
        "callisto",
    }


def test_saturn_children_include_major_moons():
    children = get_children("saturn")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "titan",
        "enceladus",
    }


def test_uranus_children_include_major_moons():
    children = get_children("uranus")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "miranda",
        "titania",
        "oberon",
    }


def test_neptune_children_include_triton():
    children = get_children("neptune")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "triton",
    }


def test_pluto_children_include_charon():
    children = get_children("pluto")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "charon",
    }


def test_moon_ancestors_include_parent_and_sun():
    ancestors = get_ancestors("moon")

    ancestor_ids = [
        ancestor.id
        for ancestor in ancestors
    ]

    assert ancestor_ids == [
        "earth",
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]


def test_charon_ancestors_include_pluto_and_sun():
    ancestors = get_ancestors("charon")

    ancestor_ids = [
        ancestor.id
        for ancestor in ancestors
    ]

    assert ancestor_ids == [
        "pluto",
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]

def test_universe_is_registered():
    universe = get_celestial_object("universe")

    assert universe is not None
    assert universe.name == "Universe"
    assert universe.object_type == "universe"
    assert universe.parent_id is None


def test_milky_way_is_registered_as_galaxy():
    milky_way = get_celestial_object("milky-way")

    assert milky_way is not None
    assert milky_way.name == "Milky Way"
    assert milky_way.object_type == "galaxy"
    assert milky_way.parent_id == "universe"


def test_solar_system_belongs_to_milky_way():
    solar_system = get_celestial_object("solar-system")

    assert solar_system is not None
    assert solar_system.parent_id == "milky-way"


def test_milky_way_children_include_solar_system():
    children = get_children("milky-way")

    child_ids = {
        child.id
        for child in children
    }

    assert child_ids == {
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    }


def test_moon_ancestors_extend_to_milky_way_and_universe():
    ancestors = get_ancestors("moon")

    ancestor_ids = [
        ancestor.id
        for ancestor in ancestors
    ]

    assert ancestor_ids == [
        "earth",
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]


def test_charon_ancestors_extend_to_milky_way_and_universe():
    ancestors = get_ancestors("charon")

    ancestor_ids = [
        ancestor.id
        for ancestor in ancestors
    ]

    assert ancestor_ids == [
        "pluto",
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]

def test_stellar_objects_are_registered():
    for object_id in (
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    ):
        obj = get_celestial_object(object_id)

        assert obj is not None
        assert obj.object_type == "star"
        assert obj.parent_id == "milky-way"


def test_milky_way_contains_registered_stars():
    children = get_children("milky-way")

    child_ids = {
        obj.id
        for obj in children
    }

    assert {
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    }.issubset(child_ids)


def test_stellar_ancestors_reach_universe():
    ancestors = get_ancestors("sirius")

    ancestor_ids = [
        obj.id
        for obj in ancestors
    ]

    assert ancestor_ids == [
        "milky-way",
        "universe",
    ]


def test_sun_remains_in_solar_system():
    sun = get_celestial_object("sun")

    assert sun is not None
    assert sun.object_type == "star"
    assert sun.parent_id == "solar-system"
