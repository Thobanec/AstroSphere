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

    execution_object_id = (
        context.object.id
        if context.object is not None
        else None
    )

    # When the question resolver identifies a concrete reference body,
    # prefer that body for capability execution whenever it supports the
    # requested capability. Universe remains the canonical fallback context.
    if (
        context.metadata
        and isinstance(
            context.metadata.get("reference_body"),
            str,
        )
    ):
        reference_body = (
            context.metadata["reference_body"]
            .strip()
            .lower()
        )

        if reference_body:
            from astrosphere.capabilities.registry import (
                get_capabilities_for_object,
            )

            reference_capabilities = {
                capability.id
                for capability in get_capabilities_for_object(
                    reference_body
                )
            }

            if capability_id in reference_capabilities:
                execution_object_id = reference_body

    if execution_object_id is None:
        raise ValueError(
            "AIContext must contain a canonical celestial object."
        )

    if (
        capability_id not in available_capabilities
        and (
            context.object is None
            or execution_object_id == context.object.id
        )
    ):
        raise ValueError(
            f"Capability is not available for the grounded "
            f"object: {capability_id}"
        )

    requested_time = (
        observation_time
        if observation_time is not None
        else context.observation_time
    )

    normalized_time = normalize_observation_time(
        requested_time
    )

    request_parameters = dict(parameters or {})

    # Carry question-resolved target information into capabilities such
    # as distance when the caller did not explicitly supply parameters.
    if (
        capability_id == "distance"
        and context.metadata
        and "target_body" in context.metadata
        and "target_body" not in request_parameters
    ):
        request_parameters["target_body"] = (
            context.metadata["target_body"]
        )

    request = CapabilityExecutionRequest(
        object_id=execution_object_id,
        capability_id=capability_id,
        observation_time=normalized_time,
        parameters=request_parameters,
    )

    return execute_capability(request)
