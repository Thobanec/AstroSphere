from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.parameters import (
    validate_capability_parameters,
)
from astrosphere.capabilities.registry import (
    get_capabilities_for_object,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)


def validate_capability_execution_request(
    request,
):
    if not isinstance(
        request,
        CapabilityExecutionRequest,
    ):
        raise TypeError(
            "Expected CapabilityExecutionRequest."
        )

    object_id = request.object_id.strip().lower()
    capability_id = request.capability_id.strip().lower()

    if not object_id:
        raise ValueError(
            "Object ID is required."
        )

    if not capability_id:
        raise ValueError(
            "Capability ID is required."
        )

    obj = get_celestial_object(object_id)

    if obj is None:
        raise ValueError(
            f"Unknown celestial object: {object_id}"
        )

    capabilities = get_capabilities_for_object(
        object_id
    )

    supported_ids = {
        capability.id
        for capability in capabilities
    }

    if capability_id not in supported_ids:
        raise ValueError(
            f"Capability '{capability_id}' is not "
            f"supported for object '{object_id}'."
        )

    parameters = validate_capability_parameters(
        capability_id,
        request.parameters,
    )

    return CapabilityExecutionRequest(
        object_id=object_id,
        capability_id=capability_id,
        observation_time=request.observation_time,
        parameters=parameters,
    )
