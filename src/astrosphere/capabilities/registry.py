from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_CONTEXT,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_RELATIONSHIPS,
    CAPABILITY_SCIENTIFIC_DATA,
    CAPABILITY_SPACE_WEATHER,
    CAPABILITY_TRACKING,
    CAPABILITY_TRAJECTORY,
    CapabilityDefinition,
)


CAPABILITY_DEFINITIONS = {

    CAPABILITY_CONTEXT: CapabilityDefinition(
        id=CAPABILITY_CONTEXT,
        name="Object Context",
        description=(
            "Provide the canonical celestial object, "
            "its hierarchy, parent, system, and connected "
            "scientific context."
        ),
        supported_object_types=(
            "system",
            "star",
            "planet",
            "dwarf_planet",
            "asteroid",
            "spacecraft",
        ),
    ),

    CAPABILITY_SCIENTIFIC_DATA: CapabilityDefinition(
        id=CAPABILITY_SCIENTIFIC_DATA,
        name="Scientific Data",
        description=(
            "Provide scientific position, velocity, "
            "observation time, and provenance for a "
            "supported celestial object."
        ),
        supported_object_types=(
            "planet",
            "dwarf_planet",
            "asteroid",
            "spacecraft",
        ),
    ),

    CAPABILITY_RELATIONSHIPS: CapabilityDefinition(
        id=CAPABILITY_RELATIONSHIPS,
        name="Relationships",
        description=(
            "Provide the canonical hierarchy, ancestors, "
            "parent, and children of a celestial object."
        ),
        supported_object_types=(
            "system",
            "star",
            "planet",
            "dwarf_planet",
            "asteroid",
            "spacecraft",
        ),
    ),

    CAPABILITY_TRACKING: CapabilityDefinition(
        id=CAPABILITY_TRACKING,
        name="Tracking",
        description=(
            "Calculate the current tracked position and "
            "motion of a supported asteroid or spacecraft."
        ),
        supported_object_types=(
            "asteroid",
            "spacecraft",
        ),
    ),

    CAPABILITY_TRAJECTORY: CapabilityDefinition(
        id=CAPABILITY_TRAJECTORY,
        name="Trajectory",
        description=(
            "Calculate a time-based trajectory for a "
            "supported asteroid."
        ),
        supported_object_ids=(
            "asteroid:99942",
        ),
    ),

    CAPABILITY_CLOSE_APPROACHES: CapabilityDefinition(
        id=CAPABILITY_CLOSE_APPROACHES,
        name="Close Approaches",
        description=(
            "Retrieve close-approach data for a supported "
            "asteroid."
        ),
        supported_object_ids=(
            "asteroid:99942",
        ),
    ),

    CAPABILITY_SPACE_WEATHER: CapabilityDefinition(
        id=CAPABILITY_SPACE_WEATHER,
        name="Space Weather",
        description=(
            "Provide current solar-wind, magnetic-field, "
            "and geomagnetic conditions associated with Earth."
        ),
        supported_object_ids=(
            "earth",
        ),
    ),

    CAPABILITY_ORBITAL_ANALYSIS: CapabilityDefinition(
        id=CAPABILITY_ORBITAL_ANALYSIS,
        name="Orbital Analysis",
        description=(
            "Analyze distance and relative motion between "
            "supported planetary bodies over a selected period."
        ),
        supported_object_types=(
            "planet",
        ),
    ),
}


def get_capability_definition(capability_id):
    return CAPABILITY_DEFINITIONS.get(
        capability_id
    )

def get_capabilities_for_object(object_id):
    from astrosphere.models.celestial_registry import get_celestial_object

    obj = get_celestial_object(object_id)

    if obj is None:
        return ()

    capabilities = []

    for capability in CAPABILITY_DEFINITIONS.values():

        if object_id in capability.supported_object_ids:
            capabilities.append(capability)
            continue

        if obj.object_type in capability.supported_object_types:
            capabilities.append(capability)

    return tuple(capabilities)

