from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_CONTEXT,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_PLANETARY_TRAJECTORY,
    CAPABILITY_RELATIONSHIPS,
    CAPABILITY_SCIENTIFIC_DATA,
    CAPABILITY_SPACE_WEATHER,
    CAPABILITY_TRACKING,
    CAPABILITY_TRAJECTORY,
)

from astrosphere.capabilities.registry import (
    get_capabilities_for_object,
)

from astrosphere.models.celestial_registry import (
    get_celestial_object,
)

from astrosphere.scientific.context import (
    get_celestial_object_context,
)
from astrosphere.scientific.relationships import (
    get_celestial_object_relationships,
)
from astrosphere.scientific.service import (
    get_scientific_data,
)
from astrosphere.scientific.space_weather import (
    get_space_weather_data,
)
from astrosphere.scientific.close_approaches import (
    get_close_approach_data,
)
from astrosphere.astronomy.asteroids import (
    track_asteroid,
    calculate_asteroid_trajectory,
)
from astrosphere.astronomy.spacecraft import (
    track_spacecraft_by_norad,
)
from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)
from astrosphere.astronomy.planetary_trajectory import (
    calculate_planetary_trajectory,
)


CAPABILITY_EXECUTOR_IDS = {
    CAPABILITY_CONTEXT: "context",
    CAPABILITY_SCIENTIFIC_DATA: "scientific-data",
    CAPABILITY_RELATIONSHIPS: "relationships",
    CAPABILITY_TRACKING: "tracking",
    CAPABILITY_TRAJECTORY: "trajectory",
    CAPABILITY_CLOSE_APPROACHES: "close-approaches",
    CAPABILITY_SPACE_WEATHER: "space-weather",
    CAPABILITY_ORBITAL_ANALYSIS: "orbital-analysis",
    CAPABILITY_PLANETARY_TRAJECTORY: "planetary-trajectory",
}


CAPABILITY_EXECUTORS = {
    CAPABILITY_CONTEXT: get_celestial_object_context,
    CAPABILITY_RELATIONSHIPS: get_celestial_object_relationships,
    CAPABILITY_SCIENTIFIC_DATA: get_scientific_data,
    CAPABILITY_SPACE_WEATHER: get_space_weather_data,
    CAPABILITY_CLOSE_APPROACHES: get_close_approach_data,
    CAPABILITY_TRAJECTORY: calculate_asteroid_trajectory,
    "asteroid-tracking": track_asteroid,
    "spacecraft-tracking": track_spacecraft_by_norad,
    CAPABILITY_ORBITAL_ANALYSIS: analyze_body_distance,
    CAPABILITY_PLANETARY_TRAJECTORY: calculate_planetary_trajectory,
}


def get_capability_executor_id(capability_id):
    return CAPABILITY_EXECUTOR_IDS.get(capability_id)


def get_capability_executor(executor_id):
    return CAPABILITY_EXECUTORS.get(executor_id)


def get_capability_executor_for_object(object_id, capability_id):
    obj = get_celestial_object(object_id)

    if obj is None:
        return None

    supported_capabilities = get_capabilities_for_object(object_id)

    if capability_id not in {
        capability.id for capability in supported_capabilities
    }:
        return None

    if capability_id == CAPABILITY_TRACKING:
        if obj.object_type == "asteroid":
            return CAPABILITY_EXECUTORS["asteroid-tracking"]

        if obj.object_type == "spacecraft":
            return CAPABILITY_EXECUTORS["spacecraft-tracking"]

        return None

    executor_id = get_capability_executor_id(capability_id)

    if executor_id is None:
        return None

    return get_capability_executor(executor_id)
