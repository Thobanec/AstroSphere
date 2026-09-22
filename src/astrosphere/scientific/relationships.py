from astrosphere.models.celestial_registry import (
    get_ancestors,
    get_celestial_object,
    get_children,
    get_parent_object,
)
from astrosphere.models.relationship import (
    RELATIONSHIP_CONTAINS,
    RELATIONSHIP_MEMBER_OF,
    RELATIONSHIP_ORBITS,
    ScientificRelationship,
)


SCIENTIFIC_RELATIONSHIPS = (
    ScientificRelationship(
        source_id="solar-system",
        relationship_type=RELATIONSHIP_MEMBER_OF,
        target_id="milky-way",
    ),
    ScientificRelationship(
        source_id="milky-way",
        relationship_type=RELATIONSHIP_MEMBER_OF,
        target_id="universe",
    ),
    ScientificRelationship(
        source_id="mercury",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="venus",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="earth",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="mars",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="jupiter",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="saturn",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="uranus",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="neptune",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="pluto",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="asteroid:99942",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="sun",
    ),
    ScientificRelationship(
        source_id="moon",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="earth",
    ),
    ScientificRelationship(
        source_id="phobos",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="mars",
    ),
    ScientificRelationship(
        source_id="deimos",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="mars",
    ),
    ScientificRelationship(
        source_id="io",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="jupiter",
    ),
    ScientificRelationship(
        source_id="europa",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="jupiter",
    ),
    ScientificRelationship(
        source_id="ganymede",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="jupiter",
    ),
    ScientificRelationship(
        source_id="callisto",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="jupiter",
    ),
    ScientificRelationship(
        source_id="titan",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="saturn",
    ),
    ScientificRelationship(
        source_id="enceladus",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="saturn",
    ),
    ScientificRelationship(
        source_id="miranda",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="uranus",
    ),
    ScientificRelationship(
        source_id="titania",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="uranus",
    ),
    ScientificRelationship(
        source_id="oberon",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="uranus",
    ),
    ScientificRelationship(
        source_id="triton",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="neptune",
    ),
    ScientificRelationship(
        source_id="charon",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="pluto",
    ),
    ScientificRelationship(
        source_id="spacecraft:25544",
        relationship_type=RELATIONSHIP_ORBITS,
        target_id="earth",
    ),
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
        "relationships": get_scientific_relationships(
            object_id
        ),
    }


def get_scientific_relationships(object_id):
    object_id = object_id.strip().lower()

    relationships = tuple(
        relationship
        for relationship in SCIENTIFIC_RELATIONSHIPS
        if relationship.source_id == object_id
    )

    contains_relationships = tuple(
        ScientificRelationship(
            source_id=object_id,
            relationship_type=RELATIONSHIP_CONTAINS,
            target_id=child.id,
        )
        for child in get_children(object_id)
    )

    return relationships + contains_relationships


def get_incoming_relationships(
    object_id,
    relationship_type=None,
):
    object_id = object_id.strip().lower()

    relationships = tuple(
        relationship
        for relationship in SCIENTIFIC_RELATIONSHIPS
        if relationship.target_id == object_id
    )

    contains_relationships = tuple(
        ScientificRelationship(
            source_id=child.id,
            relationship_type=RELATIONSHIP_CONTAINS,
            target_id=object_id,
        )
        for child in get_children(object_id)
    )

    relationships = relationships + contains_relationships

    if relationship_type is not None:
        relationships = tuple(
            relationship
            for relationship in relationships
            if relationship.relationship_type
            == relationship_type
        )

    return relationships


def get_incoming_related_objects(
    object_id,
    relationship_type=None,
):
    relationships = get_incoming_relationships(
        object_id,
        relationship_type=relationship_type,
    )

    return tuple(
        get_celestial_object(
            relationship.source_id
        )
        for relationship in relationships
        if get_celestial_object(
            relationship.source_id
        ) is not None
    )


def get_related_objects(
    object_id,
    relationship_type=None,
):
    object_id = object_id.strip().lower()

    relationships = (
        relationship
        for relationship in SCIENTIFIC_RELATIONSHIPS
        if relationship.source_id == object_id
    )

    if relationship_type is not None:
        relationships = (
            relationship
            for relationship in relationships
            if relationship.relationship_type
            == relationship_type
        )

    return tuple(
        get_celestial_object(
            relationship.target_id
        )
        for relationship in relationships
        if get_celestial_object(
            relationship.target_id
        ) is not None
    )
