from astrosphere.ai.grounding import (
    build_ai_context,
)
from astrosphere.ai.intent_selector import (
    select_capability_intents,
)
from astrosphere.ai.orchestration import (
    AICapabilityPlanItem,
    AIOrchestrationRequest,
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

    intents = select_capability_intents(
        context.question
    )

    if request.capability_ids:
        requested_capabilities = request.capability_ids
    elif intents:
        requested_capabilities = tuple(
            intent.capability_id
            for intent in intents
        )
    else:
        requested_capabilities = tuple(
            capability.id
            for capability in context.capabilities
        )

    normalized_capabilities = tuple(
        capability_id.strip().lower()
        for capability_id in requested_capabilities
        if isinstance(capability_id, str)
        and capability_id.strip()
    )

    intent_reasons = {
        intent.capability_id: intent.reason
        for intent in intents
    }

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

        reason = intent_reasons.get(
            capability_id,
            f"Capability selected for the question: "
            f"{context.question}",
        )

        plan.append(
            AICapabilityPlanItem(
                capability_id=capability_id,
                reason=reason,
                parameters=request.parameters,
                execution_order=execution_order,
            )
        )

    return tuple(plan)
