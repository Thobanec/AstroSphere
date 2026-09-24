from astrosphere.ai.context import AIContext, AIObjectGraph
from astrosphere.ai.entity_resolution import resolve_object_or_default
from astrosphere.ai.time import normalize_observation_time
from astrosphere.capabilities.registry import get_capabilities_for_object
from astrosphere.models.celestial_registry import get_celestial_object
from astrosphere.scientific.context import get_celestial_object_context
from astrosphere.scientific.relationships import get_celestial_object_relationships, get_incoming_relationships


def build_ai_context(question, object_id=None, observation_time=None, metadata=None, for_planning=False):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("AI question is required.")
    # An explicitly supplied object_id must refer to a real registered
    # celestial object. Do not silently replace an invalid explicit ID
    # with an object inferred from the question.
    if object_id is not None:
        if not isinstance(object_id, str) or not object_id.strip():
            raise ValueError("Celestial object ID is required.")

        explicit_object_id = object_id.strip().lower()

        if get_celestial_object(explicit_object_id) is None:
            raise ValueError(
                f"Unknown celestial object: {explicit_object_id}"
            )

    resolution = resolve_object_or_default(
        question,
        explicit_object_id=object_id,
    )

    # Preserve the existing grounding contract: when the caller does not
    # explicitly select a celestial object, the primary context remains
    # Universe. Question entities are still retained below for AI reasoning
    # and capability routing.
    if object_id is None:
        context_object_id = "universe"
    else:
        # An explicitly supplied object is authoritative. Any additional
        # entity found in the question remains available as target metadata.
        context_object_id = explicit_object_id

    if not isinstance(context_object_id, str) or not context_object_id.strip():
        raise ValueError("A canonical question context could not be resolved.")

    context_object_id = context_object_id.strip().lower()
    normalized_time = normalize_observation_time(observation_time)
    resolved_metadata = dict(metadata) if metadata else {}

    # Preserve question-resolved entities for both question-first and
    # explicitly grounded requests. An explicit object remains the subject;
    # additional question entities can represent targets.
    if resolution.entities:
        resolved_metadata.setdefault(
            "resolved_entities",
            tuple(resolution.entities),
        )

    if object_id is None:
        if resolution.reference_object_id is not None:
            resolved_metadata.setdefault(
                "reference_body",
                resolution.reference_object_id,
            )
    else:
        resolved_metadata["reference_body"] = explicit_object_id

    if resolution.target_object_id is not None:
        resolved_metadata.setdefault(
            "target_body",
            resolution.target_object_id,
        )
    celestial_object = get_celestial_object(context_object_id)
    if celestial_object is None:
        raise ValueError(f"Unknown celestial object: {context_object_id}")
    if for_planning:
        # Planning must remain lightweight. The planner only needs the
        # resolved object, capabilities, relationships and question metadata.
        # Avoid loading expensive live scientific context here because the
        # selected capability will retrieve its own data during execution.
        scientific_data = None
    else:
        celestial_context = get_celestial_object_context(
            context_object_id,
            observation_time=normalized_time,
        )
        scientific_data = celestial_context.get("scientific_data")
    capabilities = get_capabilities_for_object(context_object_id)
    provenance = tuple(scientific_data.provenance.sources) if scientific_data is not None and scientific_data.provenance is not None else ()
    relationship_context = get_celestial_object_relationships(context_object_id)
    object_graph = AIObjectGraph(
        object=relationship_context["object"], parent=relationship_context["parent"],
        ancestors=tuple(relationship_context["ancestors"]), children=tuple(relationship_context["children"]),
        relationships=tuple(relationship_context["relationships"]), incoming_relationships=tuple(get_incoming_relationships(context_object_id)),
    )
    return AIContext(
        question=question.strip(), observation_time=normalized_time, object=celestial_object,
        scientific_data=scientific_data, capabilities=tuple(capabilities), provenance=provenance,
        object_graph=object_graph, metadata=(resolved_metadata if resolved_metadata else None),
    )
