from astrosphere.models.relationship import (
    RELATIONSHIP_CONTAINS,
    RELATIONSHIP_MEMBER_OF,
    RELATIONSHIP_ORBITS,
    ScientificRelationship,
)
from astrosphere.scientific.relationships import (
    get_celestial_object_relationships,
    get_incoming_relationships,
    get_incoming_related_objects,
    get_related_objects,
    get_scientific_relationships,
)


def test_earth_orbits_sun():
    relationships = get_scientific_relationships("earth")

    assert relationships[0] == ScientificRelationship(
        source_id="earth",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    )

    assert [
        relationship.target_id
        for relationship in relationships
        if relationship.relationship_type == RELATIONSHIP_CONTAINS
    ] == [
        "moon",
        "spacecraft:25544",
    ]


def test_earth_relationships_include_orbit_target():
    related = get_related_objects("earth")

    assert [obj.id for obj in related] == [
        "sun",
    ]


def test_iss_orbits_earth():
    relationships = get_scientific_relationships(
        "spacecraft:25544"
    )

    assert relationships == (
        ScientificRelationship(
            source_id="spacecraft:25544",
            relationship_type=RELATIONSHIP_ORBITS,
            target_id="earth",
        ),
    )


def test_apophis_orbits_sun():
    relationships = get_scientific_relationships(
        "asteroid:99942"
    )

    assert relationships == (
        ScientificRelationship(
            source_id="asteroid:99942",
            relationship_type=RELATIONSHIP_ORBITS,
            target_id="sun",
        ),
    )


def test_relationship_service_preserves_hierarchy():
    result = get_celestial_object_relationships(
        "earth"
    )

    assert result["object"].id == "earth"
    assert result["parent"].id == "sun"

    assert "sun" in [
        ancestor.id
        for ancestor in result["ancestors"]
    ]

    assert "solar-system" in [
        ancestor.id
        for ancestor in result["ancestors"]
    ]

    assert len(result["relationships"]) == 3

    assert (
        result["relationships"][0].relationship_type
        == RELATIONSHIP_ORBITS
    )

    assert [
        relationship.target_id
        for relationship in result["relationships"]
        if relationship.relationship_type
        == RELATIONSHIP_CONTAINS
    ] == [
        "moon",
        "spacecraft:25544",
    ]


def test_unknown_relationship_object():
    assert get_scientific_relationships(
        "unknown"
    ) == ()


def test_relationship_type_filter():
    related = get_related_objects(
        "earth",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [obj.id for obj in related] == [
        "sun",
    ]

def test_sun_has_planets_as_incoming_orbit_relationships():
    related = get_incoming_related_objects(
        "sun",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    related_ids = [
        obj.id
        for obj in related
    ]

    assert related_ids == [
        "mercury",
        "venus",
        "earth",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
        "asteroid:99942",
    ]


def test_earth_has_moon_and_iss_as_incoming_orbit_relationships():
    related = get_incoming_related_objects(
        "earth",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "moon",
        "spacecraft:25544",
    ]


def test_moon_orbits_earth():
    related = get_related_objects(
        "moon",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "earth",
    ]


def test_mars_has_phobos_and_deimos_as_incoming_orbit_relationships():
    related = get_incoming_related_objects(
        "mars",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "phobos",
        "deimos",
    ]


def test_jupiter_has_four_major_moons_as_incoming_orbit_relationships():
    related = get_incoming_related_objects(
        "jupiter",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "io",
        "europa",
        "ganymede",
        "callisto",
    ]


def test_saturn_has_two_major_moons_as_incoming_orbit_relationships():
    related = get_incoming_related_objects(
        "saturn",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "titan",
        "enceladus",
    ]


def test_uranus_has_three_major_moons_as_incoming_orbit_relationships():
    related = get_incoming_related_objects(
        "uranus",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "miranda",
        "titania",
        "oberon",
    ]


def test_neptune_has_triton_as_incoming_orbit_relationship():
    related = get_incoming_related_objects(
        "neptune",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "triton",
    ]


def test_pluto_has_charon_as_incoming_orbit_relationship():
    related = get_incoming_related_objects(
        "pluto",
        relationship_type=RELATIONSHIP_ORBITS,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "charon",
    ]

def test_solar_system_is_member_of_milky_way():
    relationships = get_scientific_relationships("solar-system")

    member_of = [
        relationship
        for relationship in relationships
        if relationship.relationship_type == RELATIONSHIP_MEMBER_OF
    ]

    assert member_of == [
        ScientificRelationship(
            source_id="solar-system",
            relationship_type=RELATIONSHIP_MEMBER_OF,
            target_id="milky-way",
        ),
    ]

    assert [
        relationship.target_id
        for relationship in relationships
        if relationship.relationship_type == RELATIONSHIP_CONTAINS
    ] == [
        "sun",
        "asteroid:99942",
    ]


def test_milky_way_is_member_of_universe():
    relationships = get_scientific_relationships("milky-way")

    member_of = [
        relationship
        for relationship in relationships
        if relationship.relationship_type == RELATIONSHIP_MEMBER_OF
    ]

    assert member_of == [
        ScientificRelationship(
            source_id="milky-way",
            relationship_type=RELATIONSHIP_MEMBER_OF,
            target_id="universe",
        ),
    ]

    assert [
        relationship.target_id
        for relationship in relationships
        if relationship.relationship_type == RELATIONSHIP_CONTAINS
    ] == [
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    ]


def test_solar_system_related_object_is_milky_way():
    related = get_related_objects(
        "solar-system",
        relationship_type=RELATIONSHIP_MEMBER_OF,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "milky-way",
    ]


def test_milky_way_related_object_is_universe():
    related = get_related_objects(
        "milky-way",
        relationship_type=RELATIONSHIP_MEMBER_OF,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "universe",
    ]


def test_milky_way_has_solar_system_as_incoming_member():
    related = get_incoming_related_objects(
        "milky-way",
        relationship_type=RELATIONSHIP_MEMBER_OF,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "solar-system",
    ]


def test_universe_has_milky_way_as_incoming_member():
    related = get_incoming_related_objects(
        "universe",
        relationship_type=RELATIONSHIP_MEMBER_OF,
    )

    assert [
        obj.id
        for obj in related
    ] == [
        "milky-way",
    ]

def test_milky_way_contains_registered_children():
    relationships = get_scientific_relationships(
        "milky-way"
    )

    contains = [
        relationship.target_id
        for relationship in relationships
        if relationship.relationship_type
        == RELATIONSHIP_CONTAINS
    ]

    assert contains == [
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    ]


def test_earth_contains_registered_children():
    relationships = get_scientific_relationships(
        "earth"
    )

    contains = [
        relationship.target_id
        for relationship in relationships
        if relationship.relationship_type
        == RELATIONSHIP_CONTAINS
    ]

    assert contains == [
        "moon",
        "spacecraft:25544",
    ]


def test_earth_relationships_preserve_orbit_and_contains():
    relationships = get_scientific_relationships(
        "earth"
    )

    assert relationships == (
        ScientificRelationship(
            source_id="earth",
            relationship_type=RELATIONSHIP_ORBITS,
            target_id="sun",
        ),
        ScientificRelationship(
            source_id="earth",
            relationship_type="contains",
            target_id="moon",
        ),
        ScientificRelationship(
            source_id="earth",
            relationship_type="contains",
            target_id="spacecraft:25544",
        ),
    )

def test_milky_way_has_incoming_contains_relationships():
    related = get_incoming_related_objects(
        "milky-way",
        relationship_type=RELATIONSHIP_CONTAINS,
    )

    assert [obj.id for obj in related] == [
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    ]


def test_earth_has_incoming_contains_relationships():
    related = get_incoming_related_objects(
        "earth",
        relationship_type=RELATIONSHIP_CONTAINS,
    )

    assert [obj.id for obj in related] == [
        "moon",
        "spacecraft:25544",
    ]


def test_incoming_contains_relationships_are_derived_from_registry():
    relationships = get_incoming_relationships(
        "earth",
        relationship_type=RELATIONSHIP_CONTAINS,
    )

    assert relationships == (
        ScientificRelationship(
            source_id="moon",
            relationship_type=RELATIONSHIP_CONTAINS,
            target_id="earth",
        ),
        ScientificRelationship(
            source_id="spacecraft:25544",
            relationship_type=RELATIONSHIP_CONTAINS,
            target_id="earth",
        ),
    )
