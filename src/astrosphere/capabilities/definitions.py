from dataclasses import dataclass


CAPABILITY_CONTEXT = "context"

CAPABILITY_SCIENTIFIC_DATA = "scientific-data"

CAPABILITY_RELATIONSHIPS = "relationships"

CAPABILITY_TRACKING = "tracking"

CAPABILITY_TRAJECTORY = "trajectory"

CAPABILITY_CLOSE_APPROACHES = "close-approaches"

CAPABILITY_SPACE_WEATHER = "space-weather"

CAPABILITY_ORBITAL_ANALYSIS = "orbital-analysis"

CAPABILITY_PLANETARY_TRAJECTORY = "planetary-trajectory"


@dataclass(frozen=True)
class CapabilityDefinition:

    id: str
    name: str
    description: str
    supported_object_types: tuple[str, ...] = ()
    supported_object_ids: tuple[str, ...] = ()
