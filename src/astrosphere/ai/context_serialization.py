from dataclasses import is_dataclass
from datetime import datetime

from astrosphere.ai.context import AIContext
from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretation,
    AIInterpretationSet,
)
from astrosphere.models.celestial_serialization import (
    celestial_object_to_dict,
)
from astrosphere.models.scientific_serialization import (
    scientific_data_to_dict,
    space_weather_data_to_dict,
)


def _observation_time_to_string(observation_time):
    if observation_time is None:
        return None

    if isinstance(observation_time, datetime):
        return observation_time.isoformat()

    return str(observation_time)


def _relationship_to_dict(relationship):
    return {
        "source_id": relationship.source_id,
        "relationship_type": relationship.relationship_type,
        "target_id": relationship.target_id,
    }


def _capability_to_dict(capability):
    return {
        "id": capability.id,
        "name": capability.name,
        "description": capability.description,
        "supported_object_types": list(
            capability.supported_object_types
        ),
        "supported_object_ids": list(
            capability.supported_object_ids
        ),
    }


def _serialize_capability_value(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _serialize_capability_value(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            _serialize_capability_value(item)
            for item in value
        ]

    if hasattr(value, "id") and hasattr(value, "object_type"):
        return celestial_object_to_dict(value)

    if hasattr(value, "object_id") and hasattr(value, "provenance"):
        return scientific_data_to_dict(value)

    if hasattr(value, "observation_time") and hasattr(
        value,
        "solar_wind",
    ):
        return space_weather_data_to_dict(value)

    if is_dataclass(value):
        return {
            field_name: _serialize_capability_value(
                getattr(value, field_name)
            )
            for field_name in value.__dataclass_fields__
        }

    return value


def _capability_result_to_dict(result):
    return {
        "object_id": result.object_id,
        "capability_id": result.capability_id,
        "result": _serialize_capability_value(
            result.result
        ),
        "metadata": _serialize_capability_value(
            result.metadata
        ),
    }


def _data_source_to_dict(source):
    if source is None:
        return None

    return {
        "name": source.name,
        "provider": source.provider,
        "url": source.url,
        "dataset": source.dataset,
        "version": source.version,
        "upstream_source": source.upstream_source,
    }


def _object_graph_to_dict(graph):
    if graph is None:
        return None

    return {
        "object": celestial_object_to_dict(
            graph.object
        ),
        "parent": (
            celestial_object_to_dict(graph.parent)
            if graph.parent is not None
            else None
        ),
        "ancestors": [
            celestial_object_to_dict(ancestor)
            for ancestor in graph.ancestors
        ],
        "children": [
            celestial_object_to_dict(child)
            for child in graph.children
        ],
        "relationships": [
            _relationship_to_dict(relationship)
            for relationship in graph.relationships
        ],
        "incoming_relationships": [
            _relationship_to_dict(relationship)
            for relationship in graph.incoming_relationships
        ],
    }


def _fact_to_dict(fact):
    if not isinstance(fact, AIFact):
        raise ValueError("AIFact is required.")

    return {
        "name": fact.name,
        "value": _serialize_capability_value(fact.value),
        "unit": fact.unit,
        "source_capability": fact.source_capability,
        "source": _data_source_to_dict(fact.source),
        "metadata": _serialize_capability_value(fact.metadata),
    }


def _fact_set_to_dict(fact_set):
    if fact_set is None:
        return None

    if not isinstance(fact_set, AIFactSet):
        raise ValueError("AIFactSet is required.")

    return {
        "object_id": fact_set.object_id,
        "facts": [
            _fact_to_dict(fact)
            for fact in fact_set.facts
        ],
        "observation_time": _observation_time_to_string(
            fact_set.observation_time
        ),
        "provenance": [
            _data_source_to_dict(source)
            for source in fact_set.provenance
        ],
        "uncertainties": list(
            fact_set.uncertainties
        ),
    }


def _interpretation_to_dict(interpretation):
    if not isinstance(
        interpretation,
        AIInterpretation,
    ):
        raise ValueError(
            "AIInterpretation is required."
        )

    return {
        "subject": interpretation.subject,
        "statement": interpretation.statement,
        "supporting_facts": list(
            interpretation.supporting_facts
        ),
        "supporting_capabilities": list(
            interpretation.supporting_capabilities
        ),
        "observation_time": _observation_time_to_string(
            interpretation.observation_time
        ),
        "provenance": [
            _data_source_to_dict(source)
            for source in interpretation.provenance
        ],
        "uncertainties": list(
            interpretation.uncertainties
        ),
    }


def _interpretation_set_to_dict(
    interpretation_set,
):
    if interpretation_set is None:
        return None

    if not isinstance(
        interpretation_set,
        AIInterpretationSet,
    ):
        raise ValueError(
            "AIInterpretationSet is required."
        )

    return {
        "object_id": interpretation_set.object_id,
        "interpretations": [
            _interpretation_to_dict(
                interpretation
            )
            for interpretation
            in interpretation_set.interpretations
        ],
        "observation_time": _observation_time_to_string(
            interpretation_set.observation_time
        ),
        "provenance": [
            _data_source_to_dict(source)
            for source in interpretation_set.provenance
        ],
        "uncertainties": list(
            interpretation_set.uncertainties
        ),
    }

def ai_context_to_dict(context):
    if not isinstance(context, AIContext):
        raise ValueError("AIContext is required.")

    return {
        "question": context.question,
        "observation_time": _observation_time_to_string(
            context.observation_time
        ),
        "object": (
            celestial_object_to_dict(context.object)
            if context.object is not None
            else None
        ),
        "scientific_data": (
            scientific_data_to_dict(
                context.scientific_data
            )
            if context.scientific_data is not None
            else None
        ),
        "capabilities": [
            _capability_to_dict(capability)
            for capability in context.capabilities
        ],
        "capability_results": [
            _capability_result_to_dict(result)
            for result in context.capability_results
        ],
        "provenance": [
            _data_source_to_dict(source)
            for source in context.provenance
        ],
        "uncertainties": list(context.uncertainties),
        "object_graph": _object_graph_to_dict(
            context.object_graph
        ),
        "metadata": context.metadata,
    }
