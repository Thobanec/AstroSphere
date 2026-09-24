from astrosphere.ai.grounding import build_ai_context
from astrosphere.ai.question_understanding import understand_scientific_question
from astrosphere.ai.orchestration import AICapabilityPlanItem, AIOrchestrationRequest
from astrosphere.capabilities.parameters import get_capability_parameter_names


def plan_ai_capabilities(request):
    if not isinstance(request, AIOrchestrationRequest):
        raise ValueError("AIOrchestrationRequest is required.")
    context = build_ai_context(
        request.question,
        request.object_id,
        observation_time=request.observation_time,
        metadata=request.metadata,
        for_planning=True,
    )
    available = {capability.id for capability in context.capabilities}

    # The canonical context remains Universe when no object was explicitly
    # selected. Question entity resolution may nevertheless identify a
    # concrete reference body whose capabilities are valid for the question.
    question_available = set(available)

    reference_body = None
    if (
        context.metadata
        and isinstance(context.metadata.get("reference_body"), str)
    ):
        reference_body = context.metadata["reference_body"].strip().lower()

    if reference_body:
        from astrosphere.capabilities.registry import (
            get_capabilities_for_object,
        )

        question_available.update(
            capability.id
            for capability in get_capabilities_for_object(reference_body)
        )

    understood = understand_scientific_question(
        context.question,
        object_id=context.object.id,
        available_capabilities=question_available,
    )
    intents = list(understood.intents)
    requested = tuple(request.capability_ids) if request.capability_ids else tuple(i.capability_id for i in intents)
    params = dict(request.parameters or {})

    # Question-first distance queries may resolve a target body from the
    # user's question (for example, "How far is Earth from Mars?").
    # Only propagate target_body when the distance capability is actually
    # selected. Other capabilities must not receive unsupported parameters.
    if (
        "distance" in requested
        and "target_body" not in params
        and context.metadata
    ):
        target_body = context.metadata.get("target_body")
        if target_body is not None:
            params["target_body"] = target_body
    # Natural-language orbital questions do not require the user to
    # manually provide a reference body. When the question describes a
    # body's motion around another body and only the subject is resolved,
    # default the reference frame to the Sun.
    if (
        "orbital-analysis" in requested
        and "reference_body" not in params
        and "target_body" not in params
    ):
        params["reference_body"] = "sun"
        params["target_body"] = context.object.id
    elif (
        "orbital-analysis" in requested
        and "reference_body" not in params
        and "target_body" in params
    ):
        params["reference_body"] = "sun"

    # Question-first pairwise distance. Entity resolution places target_body in params.
    if (
        "target_body" in params
        and "distance" in question_available
        and any(i == "distance" for i in requested)
    ):
        requested = ("distance",)
    if "planetary-defence" in requested and "planetary-defence" in available:
        requested = ("planetary-defence",)

    # A named asteroid close-approach question needs a future search window.
    # The close-approaches capability exposes date_min/date_max rather than
    # the planetary-defence capability's days parameter.
    if (
        "close-approaches" in requested
        and context.metadata
        and isinstance(context.metadata.get("reference_body"), str)
        and context.metadata["reference_body"].strip().lower().startswith("asteroid:")
    ):
        from datetime import date

        today = date.today()
        future = today.replace(year=today.year + 100)

        params.setdefault("date_min", today.isoformat())
        params.setdefault("date_max", future.isoformat())

    if not requested:
        # No explicit capability and no recognized intent:
        # use the complete capability set available for the resolved object.
        requested = tuple(capability.id for capability in context.capabilities)
    normalized = tuple(c.strip().lower() for c in requested if isinstance(c, str) and c.strip())
    reasons = {i.capability_id: i.reason for i in intents}
    accepted = set()
    for capability_id in normalized:
        if capability_id not in question_available:
            raise ValueError(
                f"Capability is not available for the grounded object: "
                f"{capability_id}"
            )
        accepted.update(get_capability_parameter_names(capability_id))
    unsupported = set(params) - accepted
    if unsupported:
        raise ValueError("Unsupported parameters for selected capabilities: " + ", ".join(sorted(unsupported)))
    plan=[]
    for order, capability_id in enumerate(normalized,1):
        names=get_capability_parameter_names(capability_id)
        plan.append(AICapabilityPlanItem(
            capability_id=capability_id,
            reason=reasons.get(capability_id, f"Capability selected for the question: {context.question}"),
            parameters={k:v for k,v in params.items() if k in names},
            execution_order=order,
        ))
    return tuple(plan)
