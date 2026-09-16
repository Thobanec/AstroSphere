from astrosphere.ai.capability_access import (
    execute_ai_capability,
)
from astrosphere.ai.grounding import (
    build_ai_context,
)
from astrosphere.ai.orchestration import (
    AIOrchestrationRequest,
    AIOrchestrationResult,
)


def orchestrate_ai_request(request):
    if not isinstance(
        request,
        AIOrchestrationRequest,
    ):
        raise ValueError(
            "AIOrchestrationRequest is required."
        )

    context = build_ai_context(
        request.question,
        request.object_id,
        observation_time=request.observation_time,
    )

    available_capabilities = {
        capability.id
        for capability in context.capabilities
    }

    requested_capabilities = (
        request.capability_ids
        if request.capability_ids
        else tuple(
            capability.id
            for capability in context.capabilities
        )
    )

    normalized_capabilities = tuple(
        capability_id.strip().lower()
        for capability_id in requested_capabilities
        if isinstance(capability_id, str)
        and capability_id.strip()
    )

    for capability_id in normalized_capabilities:
        if capability_id not in available_capabilities:
            raise ValueError(
                f"Capability is not available for the "
                f"grounded object: {capability_id}"
            )

    results = []

    for capability_id in normalized_capabilities:
        result = execute_ai_capability(
            context,
            capability_id,
            observation_time=request.observation_time,
            parameters=request.parameters,
        )
        results.append(result)

    return AIOrchestrationResult(
        question=context.question,
        object_id=context.object.id,
        capabilities=normalized_capabilities,
        results=tuple(results),
        observation_time=context.observation_time,
    )
