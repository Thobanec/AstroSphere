from astrosphere.ai.context import (
    AIContext,
    AIObjectGraph,
)
from astrosphere.ai.time import normalize_observation_time
from astrosphere.capabilities.registry import (
    get_capabilities_for_object,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)
from astrosphere.scientific.context import (
    get_celestial_object_context,
)
from astrosphere.scientific.relationships import (
    get_celestial_object_relationships,
    get_incoming_relationships,
)


def build_ai_context(
    question,
    object_id,
    observation_time=None,
):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("AI question is required.")

    if not isinstance(object_id, str) or not object_id.strip():
        raise ValueError("Celestial object ID is required.")

    object_id = object_id.strip().lower()

    normalized_time = normalize_observation_time(
        observation_time
    )

    celestial_object = get_celestial_object(object_id)

    if celestial_object is None:
        raise ValueError(
            f"Unknown celestial object: {object_id}"
        )

    celestial_context = get_celestial_object_context(
        object_id,
        observation_time=normalized_time,
    )

    scientific_data = celestial_context.get(
        "scientific_data"
    )

    capabilities = get_capabilities_for_object(
        object_id
    )

    provenance = ()

    if scientific_data is not None:
        if scientific_data.provenance is not None:
            provenance = tuple(
                scientific_data.provenance.sources
            )

    relationship_context = get_celestial_object_relationships(
        object_id
    )

    incoming_relationships = get_incoming_relationships(
        object_id
    )

    object_graph = AIObjectGraph(
        object=relationship_context["object"],
        parent=relationship_context["parent"],
        ancestors=tuple(
            relationship_context["ancestors"]
        ),
        children=tuple(
            relationship_context["children"]
        ),
        relationships=tuple(
            relationship_context["relationships"]
        ),
        incoming_relationships=tuple(
            incoming_relationships
        ),
    )

    return AIContext(
        question=question.strip(),
        observation_time=normalized_time,
        object=celestial_object,
        scientific_data=scientific_data,
        capabilities=tuple(capabilities),
        provenance=provenance,
        object_graph=object_graph,
    )
