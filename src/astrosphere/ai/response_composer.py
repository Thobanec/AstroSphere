from astrosphere.ai.context import AIContext
from astrosphere.ai.response import AIResponse
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def compose_ai_response(
    context,
    results,
):
    if not isinstance(context, AIContext):
        raise ValueError("AIContext is required.")

    if context.object is None:
        raise ValueError(
            "AIContext must contain a canonical celestial object."
        )

    if not isinstance(results, tuple):
        results = tuple(results)

    for result in results:
        if not isinstance(
            result,
            CapabilityExecutionResult,
        ):
            raise ValueError(
                "AI response results must be "
                "CapabilityExecutionResult instances."
            )

    answer = _compose_answer(
        context,
        results,
    )

    provenance = list(context.provenance)

    for result in results:
        result_value = result.result

        if isinstance(result_value, dict):
            result_provenance = result_value.get(
                "provenance"
            )

            if result_provenance:
                for source in result_provenance:
                    if source not in provenance:
                        provenance.append(source)

    return AIResponse(
        question=context.question,
        object_id=context.object.id,
        answer=answer,
        observation_time=context.observation_time,
        results=results,
        provenance=tuple(provenance),
        uncertainties=context.uncertainties,
    )


def _compose_answer(
    context,
    results,
):
    object_name = context.object.name

    if not results:
        return (
            f"No capability results are available for "
            f"{object_name}."
        )

    capability_ids = tuple(
        result.capability_id
        for result in results
    )

    if len(capability_ids) == 1:
        capability_id = capability_ids[0]

        return (
            f"AstroSphere retrieved the "
            f"{capability_id} result for "
            f"{object_name}."
        )

    capability_text = ", ".join(
        capability_ids
    )

    return (
        f"AstroSphere retrieved the following "
        f"capability results for {object_name}: "
        f"{capability_text}."
    )
