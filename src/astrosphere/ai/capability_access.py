from astrosphere.ai.context import AIContext
from astrosphere.ai.time import normalize_observation_time
from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.runner import execute_capability


def execute_ai_capability(
    context,
    capability_id,
    observation_time=None,
    parameters=None,
):
    if not isinstance(context, AIContext):
        raise ValueError("AIContext is required.")

    if not isinstance(capability_id, str) or not capability_id.strip():
        raise ValueError("Capability ID is required.")

    capability_id = capability_id.strip().lower()

    available_capabilities = {
        capability.id
        for capability in context.capabilities
    }

    if capability_id not in available_capabilities:
        raise ValueError(
            f"Capability is not available for the grounded "
            f"object: {capability_id}"
        )

    if context.object is None:
        raise ValueError(
            "AIContext must contain a canonical celestial object."
        )

    requested_time = (
        observation_time
        if observation_time is not None
        else context.observation_time
    )

    normalized_time = normalize_observation_time(
        requested_time
    )

    request = CapabilityExecutionRequest(
        object_id=context.object.id,
        capability_id=capability_id,
        observation_time=normalized_time,
        parameters=parameters,
    )

    return execute_capability(request)
