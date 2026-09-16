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
from astrosphere.ai.planner import (
    plan_ai_capabilities,
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

    plan = plan_ai_capabilities(request)

    results = []

    for plan_item in plan:
        result = execute_ai_capability(
            context,
            plan_item.capability_id,
            observation_time=request.observation_time,
            parameters=plan_item.parameters,
        )
        results.append(result)

    capabilities = tuple(
        plan_item.capability_id
        for plan_item in plan
    )

    return AIOrchestrationResult(
        question=context.question,
        object_id=context.object.id,
        capabilities=capabilities,
        results=tuple(results),
        observation_time=context.observation_time,
    )
