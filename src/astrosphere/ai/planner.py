from astrosphere.ai.orchestration import (
    AICapabilityPlanItem,
    AIOrchestrationRequest,
)
from astrosphere.ai.grounding import (
    build_ai_context,
)


def plan_ai_capabilities(request):
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

    plan = []

    for execution_order, capability_id in enumerate(
        normalized_capabilities,
        start=1,
    ):
        if capability_id not in available_capabilities:
            raise ValueError(
                f"Capability is not available for the "
                f"grounded object: {capability_id}"
            )

        plan.append(
            AICapabilityPlanItem(
                capability_id=capability_id,
                reason=(
                    f"Capability selected for the question: "
                    f"{context.question}"
                ),
                parameters=request.parameters,
                execution_order=execution_order,
            )
        )

    return tuple(plan)
