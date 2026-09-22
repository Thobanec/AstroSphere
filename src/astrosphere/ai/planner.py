from astrosphere.ai.grounding import (
    build_ai_context,
)
from astrosphere.ai.question_understanding import (
    understand_scientific_question,
)
from astrosphere.ai.orchestration import (
    AICapabilityPlanItem,
    AIOrchestrationRequest,
)
from astrosphere.capabilities.parameters import (
    get_capability_parameter_names,
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

    understood_question = understand_scientific_question(
        context.question,
        object_id=context.object.id,
        available_capabilities=available_capabilities,
    )

    intents = understood_question.intents

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

    request_parameters = request.parameters or {}

    accepted_parameters = set()

    for capability_id in normalized_capabilities:
        if capability_id not in available_capabilities:
            raise ValueError(
                f"Capability is not available for the "
                f"grounded object: {capability_id}"
            )

        accepted_parameters.update(
            get_capability_parameter_names(
                capability_id
            )
        )

    unsupported_parameters = (
        set(request_parameters) - accepted_parameters
    )

    if unsupported_parameters:
        names = ", ".join(
            sorted(unsupported_parameters)
        )
        raise ValueError(
            f"Unsupported parameters for selected "
            f"capabilities: {names}"
        )

    for execution_order, capability_id in enumerate(
        normalized_capabilities,
        start=1,
    ):
        reason = intent_reasons.get(
            capability_id,
            f"Capability selected for the question: "
            f"{context.question}",
        )

        capability_parameter_names = (
            get_capability_parameter_names(
                capability_id
            )
        )

        capability_parameters = {
            name: value
            for name, value in request_parameters.items()
            if name in capability_parameter_names
        }

        plan.append(
            AICapabilityPlanItem(
                capability_id=capability_id,
                reason=reason,
                parameters=capability_parameters,
                execution_order=execution_order,
            )
        )

    return tuple(plan)
