from astrosphere.ai.context import AIContext
from astrosphere.ai.fact_extractor import (
    extract_ai_facts,
)
from astrosphere.ai.interpreter import (
    interpret_ai_facts,
)
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

    facts = extract_ai_facts(
        context.object.id,
        results,
    )

    interpretations = interpret_ai_facts(
        context.object.name,
        facts,
    )

    answer = _compose_answer(
        context,
        results,
        facts,
    )

    provenance = list(context.provenance)

    for source in facts.provenance:
        if source not in provenance:
            provenance.append(source)

    return AIResponse(
        question=context.question,
        object_id=context.object.id,
        answer=answer,
        observation_time=(
            facts.observation_time
            if facts.observation_time is not None
            else context.observation_time
        ),
        results=results,
        facts=facts,
        interpretations=interpretations,
        provenance=tuple(provenance),
        uncertainties=context.uncertainties,
    )


def _render_fact(fact):
    if fact.unit:
        return (
            f"{fact.name}: "
            f"{fact.value} "
            f"{fact.unit}"
        )

    return (
        f"{fact.name}: "
        f"{fact.value}"
    )


def _render_facts(facts):
    return "\n".join(
        _render_fact(fact)
        for fact in facts.facts
    )


def _compose_answer(
    context,
    results,
    facts,
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

        answer = (
            f"AstroSphere retrieved the "
            f"{capability_id} result for "
            f"{object_name}."
        )
    else:
        capability_text = ", ".join(
            capability_ids
        )

        answer = (
            f"AstroSphere retrieved the following "
            f"capability results for {object_name}: "
            f"{capability_text}."
        )

    if not facts.facts:
        return answer

    return (
        f"{answer}\n"
        f"{_render_facts(facts)}"
    )
