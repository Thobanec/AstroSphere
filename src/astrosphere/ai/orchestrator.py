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
from astrosphere.ai.llm import (
    AILanguageProvider,
)
from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.ai.planner import (
    plan_ai_capabilities,
)
from astrosphere.ai.response_composer import (
    compose_ai_response,
)


def orchestrate_ai_request(
    request,
    language_provider: AILanguageProvider | None = None,
):
    if language_provider is None:
        language_provider = DeterministicLanguageProvider()

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

    composed_response = compose_ai_response(
        context,
        tuple(results),
        language_provider=language_provider,
    )

    capabilities = tuple(
        plan_item.capability_id
        for plan_item in plan
    )

    return AIOrchestrationResult(
        question=composed_response.question,
        object_id=composed_response.object_id,
        answer=composed_response.answer,
        capabilities=capabilities,
        results=composed_response.results,
        facts=composed_response.facts,
        interpretations=composed_response.interpretations,
        observation_time=composed_response.observation_time,
        provenance=composed_response.provenance,
        uncertainties=composed_response.uncertainties,
    )
