from dataclasses import dataclass
from typing import Any

from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_CONTEXT,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_RELATIONSHIPS,
    CAPABILITY_SCIENTIFIC_DATA,
    CAPABILITY_SPACE_WEATHER,
    CAPABILITY_TRACKING,
    CAPABILITY_TRAJECTORY,
)
from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.validation import (
    validate_capability_execution_request,
)


@dataclass(frozen=True)
class NormalizedCapabilityExecution:
    capability_id: str
    object_id: str
    arguments: tuple[Any, ...] = ()
    keyword_arguments: dict[str, Any] | None = None


def _object_numeric_id(object_id, prefix):
    if not object_id.startswith(prefix):
        raise ValueError(
            f"Object ID must start with '{prefix}'."
        )

    value = object_id[len(prefix):]

    if not value.isdigit():
        raise ValueError(
            f"Invalid numeric object ID: {object_id}"
        )

    return int(value)


def normalize_capability_request(
    request: CapabilityExecutionRequest,
):
    request = validate_capability_execution_request(
        request
    )

    parameters = request.parameters or {}
    capability_id = request.capability_id
    object_id = request.object_id

    if capability_id == CAPABILITY_CONTEXT:
        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
            arguments=(object_id,),
            keyword_arguments={
                "observation_time": request.observation_time,
            },
        )

    if capability_id == CAPABILITY_RELATIONSHIPS:
        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
            arguments=(object_id,),
        )

    if capability_id == CAPABILITY_SCIENTIFIC_DATA:
        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
            arguments=(object_id,),
            keyword_arguments={
                "observation_time": request.observation_time,
            },
        )

    if capability_id == CAPABILITY_TRACKING:
        observation_time = parameters.get(
            "observation_time",
            request.observation_time,
        )

        if object_id.startswith("asteroid:"):
            designation = _object_numeric_id(
                object_id,
                "asteroid:",
            )

            return NormalizedCapabilityExecution(
                capability_id=capability_id,
                object_id=object_id,
                arguments=(designation,),
                keyword_arguments={
                    "observation_time": observation_time,
                },
            )

        if object_id.startswith("spacecraft:"):
            norad_id = _object_numeric_id(
                object_id,
                "spacecraft:",
            )

            return NormalizedCapabilityExecution(
                capability_id=capability_id,
                object_id=object_id,
                arguments=(norad_id,),
                keyword_arguments={
                    "observation_time": observation_time,
                },
            )

        raise ValueError(
            f"Tracking is not normalizable for "
            f"object '{object_id}'."
        )

    if capability_id == CAPABILITY_TRAJECTORY:
        designation = _object_numeric_id(
            object_id,
            "asteroid:",
        )

        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
            arguments=(designation,),
            keyword_arguments={
                "observation_time": parameters.get(
                    "observation_time",
                    request.observation_time,
                ),
                "samples": parameters.get(
                    "samples",
                    181,
                ),
            },
        )

    if capability_id == CAPABILITY_CLOSE_APPROACHES:
        designation = _object_numeric_id(
            object_id,
            "asteroid:",
        )

        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
            arguments=(designation,),
            keyword_arguments={
                "date_min": parameters.get(
                    "date_min"
                ),
                "date_max": parameters.get(
                    "date_max"
                ),
            },
        )

    if capability_id == CAPABILITY_SPACE_WEATHER:
        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
        )

    if capability_id == CAPABILITY_ORBITAL_ANALYSIS:
        return NormalizedCapabilityExecution(
            capability_id=capability_id,
            object_id=object_id,
            arguments=(
                parameters["reference_body"],
                parameters["target_body"],
                parameters["start_date"],
            ),
            keyword_arguments={
                "months": parameters.get(
                    "months",
                    12,
                ),
                "interval_days": parameters.get(
                    "interval_days",
                    30,
                ),
            },
        )

    raise ValueError(
        f"Unsupported capability: {capability_id}"
    )
