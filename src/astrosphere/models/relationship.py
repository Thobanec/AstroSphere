from dataclasses import dataclass


RELATIONSHIP_ORBITS = "orbits"
RELATIONSHIP_MEMBER_OF = "member_of"
RELATIONSHIP_CONTAINS = "contains"


@dataclass(frozen=True)
class ScientificRelationship:
    source_id: str
    relationship_type: str
    target_id: str
