from astrosphere.ai.context import AIContext
from astrosphere.ai.explanation_builder import (
    build_fact_grounded_explanation,
)
from astrosphere.ai.fact_extractor import (
    extract_ai_facts,
)
from astrosphere.ai.interpreter import (
    interpret_ai_facts,
)
from astrosphere.ai.llm import (
    AILanguageRequest,
    AILanguageProvider,
)
from astrosphere.ai.response import AIResponse
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def compose_ai_response(
    context,
    results,
    language_provider: AILanguageProvider | None = None,
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

    # Resolve the object that the question is actually about.
    # Universe remains the canonical AIContext fallback, but a concrete
    # reference body identified from the question should drive response
    # facts, interpretations, explanations, and language generation.
    response_object_id = context.object.id

    if (
        context.metadata
        and isinstance(context.metadata.get("reference_body"), str)
        and context.metadata["reference_body"].strip()
    ):
        response_object_id = (
            context.metadata["reference_body"].strip().lower()
        )

    response_object = context.object

    if response_object_id != context.object.id:
        from astrosphere.models.celestial_registry import (
            get_celestial_object,
        )

        resolved_object = get_celestial_object(response_object_id)

        if resolved_object is not None:
            response_object = resolved_object

    relationship_result_present = any(
        result.capability_id == "relationships"
        for result in results
    )

    facts = extract_ai_facts(
        response_object.id,
        results,
        (
            context.object_graph
            if relationship_result_present
            else None
        ),
        question=context.question,
    )

    interpretations = interpret_ai_facts(
        response_object.name,
        facts,
    )

    explanations = _build_explanations(
        context,
        results,
        facts,
        interpretations,
    )

    # Render the answer against the question-resolved object rather than
    # the canonical Universe fallback.
    answer_context = context

    if response_object is not context.object:
        from dataclasses import replace

        answer_context = replace(
            context,
            object=response_object,
        )

    answer = _compose_answer(
        answer_context,
        results,
        facts,
    )

    provider_provenance = ()
    provider_uncertainties = ()

    if language_provider is not None:
        language_request = AILanguageRequest(
            question=answer_context.question,
            object=answer_context.object,
            facts=facts,
            interpretations=interpretations,
            explanations=explanations,
            provenance=tuple(answer_context.provenance),
            uncertainties=answer_context.uncertainties,
            observation_time=(
                facts.observation_time
                if facts.observation_time is not None
                else answer_context.observation_time
            ),
        )

        language_response = language_provider.generate(
            language_request,
        )

        answer = language_response.answer
        provider_provenance = tuple(
            language_response.provenance
        )
        provider_uncertainties = tuple(
            language_response.uncertainties
        )

    provenance = list(context.provenance)

    for source in facts.provenance:
        if source not in provenance:
            provenance.append(source)

    for source in explanations.provenance:
        if source not in provenance:
            provenance.append(source)

    for source in provider_provenance:
        if source not in provenance:
            provenance.append(source)

    uncertainties = list(context.uncertainties)

    for uncertainty in explanations.uncertainties:
        if uncertainty not in uncertainties:
            uncertainties.append(uncertainty)

    for uncertainty in provider_uncertainties:
        if uncertainty not in uncertainties:
            uncertainties.append(uncertainty)

    return AIResponse(
        question=context.question,
        object_id=response_object_id,
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
        uncertainties=tuple(uncertainties),
    )


def _build_explanations(
    context,
    results,
    facts,
    interpretations,
):
    if not facts.facts:
        return _empty_explanation_set(
            context.object.id,
        )

    subjects = []

    fact_names = {
        fact.name
        for fact in facts.facts
    }

    if any(
        name.startswith("position_")
        for name in fact_names
    ):
        subjects.append("position")

    if any(
        name.startswith("velocity_")
        for name in fact_names
    ):
        subjects.append("velocity")

    capability_ids = {
        result.capability_id
        for result in results
    }

    if (
        "trajectory" in capability_ids
        or "planetary-trajectory" in capability_ids
    ):
        subjects.append("trajectory")

    if "close-approaches" in capability_ids:
        subjects.append("close_approach")

    if "space-weather" in capability_ids:
        subjects.append("space_weather")

    if "relationships" in capability_ids:
        subjects.append("relationships")

    unique_subjects = tuple(
        dict.fromkeys(subjects)
    )

    explanations = []

    for subject in unique_subjects:
        try:
            explanation_set = (
                build_fact_grounded_explanation(
                    context.object.id,
                    facts,
                    interpretations,
                    subject,
                )
            )
        except ValueError:
            continue

        explanations.extend(
            explanation_set.explanations
        )

    if not explanations:
        return _empty_explanation_set(
            context.object.id,
        )

    provenance = tuple(
        source
        for source in (
            explanations[0].provenance
        )
    )

    uncertainties = tuple(
        dict.fromkeys(
            uncertainty
            for explanation in explanations
            for uncertainty
            in explanation.uncertainties
        )
    )

    observation_time = next(
        (
            explanation.observation_time
            for explanation in explanations
            if explanation.observation_time is not None
        ),
        None,
    )

    from astrosphere.ai.explanation import (
        AIExplanationSet,
    )

    return AIExplanationSet(
        object_id=context.object.id,
        explanations=tuple(explanations),
        level="standard",
        observation_time=observation_time,
        provenance=provenance,
        uncertainties=uncertainties,
    )


def _empty_explanation_set(object_id):
    from astrosphere.ai.explanation import (
        AIExplanationSet,
    )

    return AIExplanationSet(
        object_id=object_id,
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
