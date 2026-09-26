from datetime import datetime, timezone

from flask import (
    Blueprint,
    jsonify,
    request,
)

from astrosphere.astronomy.asteroids import (
    AsteroidDataError,
    AsteroidNotFoundError,
    AsteroidServiceError,
    calculate_asteroid_trajectory,
    track_asteroid,
)

from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)

from astrosphere.astronomy.planets import (
    PLANET_LOOKUP,
    PLANETS,
)

from astrosphere.astronomy.planetary_trajectory import (
    calculate_planetary_trajectory,
)
from astrosphere.astronomy.spacecraft import (
    SpacecraftNotFoundError,
    SpacecraftServiceError,
    track_spacecraft_by_norad,
)

from astrosphere.models.celestial_registry import (
    CELESTIAL_OBJECTS,
    CELESTIAL_OBJECT_LOOKUP,
)

from astrosphere.models.celestial_serialization import (
    celestial_object_to_dict,
)
from astrosphere.models.celestial_context_serialization import (
    celestial_object_context_to_dict,
)

from astrosphere.overview import (
    generate_solar_system_overview,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
    get_children,
    get_ancestors,
)
from astrosphere.models.scientific_serialization import (
    scientific_data_to_dict,
    space_weather_data_to_dict,
)
from astrosphere.models.close_approach_serialization import (
    close_approach_to_dict,
)
from astrosphere.scientific.asteroids import (
    get_asteroid_scientific_data,
)
from astrosphere.scientific.spacecraft import (
    get_spacecraft_scientific_data,
)
from astrosphere.scientific.close_approaches import (
    get_close_approach_data,
)
from astrosphere.scientific.context import (
    get_celestial_object_context,
)
from astrosphere.scientific.relationships import (
    get_celestial_object_relationships,
)
from astrosphere.scientific.earth import (
    get_earth_context,
)
from astrosphere.scientific.space_weather import (
    get_space_weather_data,
)
from astrosphere.scientific.service import (
    get_scientific_data,
)
from astrosphere.monitoring.service import (
    acknowledge_monitoring_alert,
    get_monitoring_status,
    list_monitoring_alerts,
    list_monitoring_events,
)
from astrosphere.capabilities import (
    get_capabilities_for_object,
)
from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.runner import (
    execute_capability,
)
from astrosphere.ai import (
    build_ai_context,
)
from astrosphere.ai.assistant import (
    process_assistant_message,
)
from astrosphere.ai.context_serialization import (
    ai_context_to_dict,
    _capability_result_to_dict,
    _fact_set_to_dict,
    _interpretation_set_to_dict,
    _observation_time_to_string,
)
from astrosphere.ai.conversation import (
    AIConversation,
    AssistantMessage,
)
from astrosphere.ai.orchestrator import (
    orchestrate_ai_request,
)
from astrosphere.ai.orchestration import (
    AIOrchestrationRequest,
)
from astrosphere.ai.provider_factory import (
    create_language_provider,
)


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api/v1",
)


@api.get("/celestial-objects")
def celestial_objects():

    return jsonify(
        {
            "status": "success",
            "data": {
                "count": len(CELESTIAL_OBJECTS),
                "objects": [
                    celestial_object_to_dict(obj)
                    for obj in CELESTIAL_OBJECTS
                ],
            },
        }
    )


@api.get("/celestial-objects/<object_id>")
def celestial_object_detail(object_id):

    object_id = object_id.strip().lower()

    obj = CELESTIAL_OBJECT_LOOKUP.get(object_id)

    if obj:
        return jsonify(
                {
                    "status": "success",
                    "data": celestial_object_to_dict(obj),
                }
            )

    return jsonify(
        {
            "status": "error",
            "error": "Celestial object was not found.",
        }
    ), 404


@api.get("/celestial-objects/<object_id>/capabilities")
def celestial_object_capabilities(object_id):
    object_id = object_id.strip().lower()

    obj = get_celestial_object(object_id)

    if obj is None:
        return jsonify(
            {
                "error": "Unknown celestial object.",
            }
        ), 404

    capabilities = get_capabilities_for_object(object_id)

    return jsonify(
        {
            "status": "success",
            "data": {
                "object": celestial_object_to_dict(obj),
                "count": len(capabilities),
                "capabilities": [
                    {
                        "id": capability.id,
                        "name": capability.name,
                        "description": capability.description,
                    }
                    for capability in capabilities
                ],
            },
        }
    )


@api.post("/capabilities/execute")
def capability_execute():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "status": "error",
                "error": "Request body must be a JSON object.",
            }
        ), 400

    object_id = data.get("object_id")
    capability_id = data.get("capability_id")

    if not isinstance(object_id, str) or not object_id.strip():
        return jsonify(
            {
                "status": "error",
                "error": "Object ID is required.",
            }
        ), 400

    if not isinstance(capability_id, str) or not capability_id.strip():
        return jsonify(
            {
                "status": "error",
                "error": "Capability ID is required.",
            }
        ), 400

    request_object = CapabilityExecutionRequest(
        object_id=object_id,
        capability_id=capability_id,
        observation_time=data.get("observation_time"),
        parameters=data.get("parameters"),
    )

    try:
        execution_result = execute_capability(
            request_object
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 400

    return jsonify(
        {
            "status": "success",
            "data": {
                "object_id": execution_result.object_id,
                "capability_id": execution_result.capability_id,
                "result": execution_result.result,
                "metadata": execution_result.metadata,
            },
        }
    )



@api.post(
    "/celestial-objects/<object_id>/capabilities/"
    "<capability_id>/execute"
)
def execute_celestial_capability(
    object_id,
    capability_id,
):
    object_id = object_id.strip().lower()
    capability_id = capability_id.strip().lower()

    data = request.get_json(silent=True)

    if data is None:
        data = {}

    if not isinstance(data, dict):
        return jsonify(
            {
                "status": "error",
                "error": "Request body must be a JSON object.",
            }
        ), 400

    parameters = data.get("parameters", {})

    if not isinstance(parameters, dict):
        return jsonify(
            {
                "status": "error",
                "error": "parameters must be an object.",
            }
        ), 400

    observation_time = data.get("observation_time")

    if (
        observation_time is not None
        and not isinstance(observation_time, str)
    ):
        return jsonify(
            {
                "status": "error",
                "error": "observation_time must be a string.",
            }
        ), 400

    request_object = CapabilityExecutionRequest(
        object_id=object_id,
        capability_id=capability_id,
        observation_time=observation_time,
        parameters=parameters,
    )

    try:
        execution_result = execute_capability(
            request_object
        )
    except (TypeError, ValueError) as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 400

    return jsonify(
        {
            "status": "success",
            "data": _capability_result_to_dict(
                execution_result
            ),
        }
    )

@api.get("/celestial-objects/<object_id>/context")
def celestial_object_context(object_id):
    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time",
            "",
        ).strip()
    )

    if observation_time_text:
        try:
            normalized_time = (
                observation_time_text.replace(
                    "Z",
                    "+00:00",
                )
            )

            observation_time = datetime.fromisoformat(
                normalized_time
            )

            if observation_time.tzinfo is None:
                observation_time = (
                    observation_time.replace(
                        tzinfo=timezone.utc
                    )
                )
            else:
                observation_time = (
                    observation_time.astimezone(
                        timezone.utc
                    )
                )

        except ValueError:
            return jsonify(
                {
                    "error": (
                        "Invalid observation_time. "
                        "Use ISO-8601 format."
                    ),
                }
            ), 400

    try:
        context = get_celestial_object_context(
            object_id,
            observation_time=observation_time,
        )

    except ValueError as exc:
        return jsonify(
            {
                "error": str(exc),
            }
        ), 404

    return jsonify(
        {
            "status": "success",
            "data": celestial_object_context_to_dict(
                context
            ),
        }
    )


@api.get("/celestial-objects/<object_id>/ai-context")
def celestial_object_ai_context(object_id):
    object_id = object_id.strip().lower()

    question = request.args.get(
        "question",
        "",
    ).strip()

    if not question:
        question = (
            f"Provide the scientific context "
            f"for {object_id}."
        )

    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time",
            "",
        ).strip()
    )

    if observation_time_text:
        observation_time = observation_time_text

    try:
        context = build_ai_context(
            question,
            object_id,
            observation_time=observation_time,
        )
    except ValueError as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 404

    return jsonify(
        {
            "status": "success",
            "data": ai_context_to_dict(context),
        }
    )


@api.get("/celestial-objects/<object_id>/graph")
def celestial_object_graph(object_id):
    object_id = object_id.strip().lower()

    try:
        graph_data = get_celestial_object_relationships(
            object_id
        )
    except ValueError:
        return jsonify(
            {
                "status": "error",
                "error": "Celestial object was not found.",
            }
        ), 404

    obj = graph_data["object"]
    parent = graph_data["parent"]

    return jsonify(
        {
            "status": "success",
            "data": {
                "id": obj.id,
                "name": obj.name,
                "object_type": obj.object_type,
                "parent": (
                    {
                        "id": parent.id,
                        "name": parent.name,
                        "object_type": parent.object_type,
                    }
                    if parent
                    else None
                ),
                "ancestors": [
                    {
                        "id": ancestor.id,
                        "name": ancestor.name,
                        "object_type": ancestor.object_type,
                    }
                    for ancestor in graph_data["ancestors"]
                ],
                "children": [
                    {
                        "id": child.id,
                        "name": child.name,
                        "object_type": child.object_type,
                    }
                    for child in graph_data["children"]
                ],
                "relationships": [
                    {
                        "source_id": relationship.source_id,
                        "relationship_type": (
                            relationship.relationship_type
                        ),
                        "target_id": relationship.target_id,
                    }
                    for relationship in graph_data[
                        "relationships"
                    ]
                ],
            },
        }
    )

@api.get("/celestial-objects/<object_id>/ancestors")
def celestial_object_ancestors(object_id):
    object_id = object_id.strip().lower()

    obj = get_celestial_object(object_id)

    if obj is None:
        return jsonify(
            {
                "status": "error",
                "error": "Celestial object was not found.",
            }
        ), 404

    ancestors = get_ancestors(object_id)

    return jsonify(
        {
            "status": "success",
            "data": {
                "id": obj.id,
                "name": obj.name,
                "ancestors": [
                    {
                        "id": ancestor.id,
                        "name": ancestor.name,
                        "object_type": ancestor.object_type,
                    }
                    for ancestor in ancestors
                ],
            },
        }
    )

@api.get("/celestial-objects/<object_id>/children")
def celestial_object_children(object_id):
    object_id = object_id.strip().lower()

    obj = get_celestial_object(object_id)

    if obj is None:
        return jsonify(
            {
                "status": "error",
                "error": "Celestial object was not found.",
            }
        ), 404

    children = get_children(object_id)

    return jsonify(
        {
            "status": "success",
            "data": {
                "id": obj.id,
                "name": obj.name,
                "children": [
                    {
                        "id": child.id,
                        "name": child.name,
                        "object_type": child.object_type,
                    }
                    for child in children
                ],
            },
        }
    )

@api.get("/celestial-objects/<object_id>/relationships")
def celestial_object_relationships(object_id):
    object_id = object_id.strip().lower()

    relationship_type = request.args.get(
        "relationship_type"
    )

    if relationship_type is not None:
        relationship_type = relationship_type.strip().lower()

    try:
        relationship_data = (
            get_celestial_object_relationships(
                object_id
            )
        )
    except ValueError:
        return jsonify(
            {
                "status": "error",
                "error": "Celestial object was not found.",
            }
        ), 404

    obj = relationship_data["object"]
    parent = relationship_data["parent"]

    relationships = relationship_data["relationships"]

    if relationship_type is not None:
        relationships = tuple(
            relationship
            for relationship in relationships
            if relationship.relationship_type == relationship_type
        )

    return jsonify(
        {
            "status": "success",
            "data": {
                "id": obj.id,
                "name": obj.name,
                "parent": (
                    {
                        "id": parent.id,
                        "name": parent.name,
                    }
                    if parent
                    else None
                ),
                "ancestors": [
                    {
                        "id": ancestor.id,
                        "name": ancestor.name,
                    }
                    for ancestor in relationship_data[
                        "ancestors"
                    ]
                ],
                "children": [
                    {
                        "id": child.id,
                        "name": child.name,
                        "object_type": child.object_type,
                    }
                    for child in relationship_data[
                        "children"
                    ]
                ],
                "relationships": [
                    {
                        "source_id": relationship.source_id,
                        "relationship_type": (
                            relationship.relationship_type
                        ),
                        "target_id": relationship.target_id,
                    }
                    for relationship in relationships
                ],
            },
        }
    )

@api.get("/celestial-objects/<object_id>/scientific-data")
def celestial_object_scientific_data(object_id):
    obj = get_celestial_object(object_id)

    if obj is None:
        return jsonify(
            {
                "error": "Unknown celestial object.",
            }
        ), 404

    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time",
            "",
        ).strip()
    )

    if observation_time_text:
        try:
            normalized_time = (
                observation_time_text.replace(
                    "Z",
                    "+00:00",
                )
            )

            observation_time = (
                datetime.fromisoformat(
                    normalized_time
                )
            )

            if observation_time.tzinfo is None:
                observation_time = (
                    observation_time.replace(
                        tzinfo=timezone.utc
                    )
                )
            else:
                observation_time = (
                    observation_time.astimezone(
                        timezone.utc
                    )
                )

        except ValueError:
            return jsonify(
                {
                    "error": (
                        "Invalid observation_time. "
                        "Use ISO-8601 format."
                    )
                }
            ), 400

    try:
        scientific_data = get_scientific_data(
            obj.id,
            observation_time=observation_time,
        )

    except ValueError as exc:
        return jsonify(
            {
                "error": str(exc),
            }
        ), 400

    return jsonify(
        {
            "status": "success",
            "data": scientific_data_to_dict(
                scientific_data
            ),
        }
    )


@api.get("/earth/context")
def earth_context():

    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time",
            "",
        ).strip()
    )

    if observation_time_text:
        try:
            normalized_time = (
                observation_time_text.replace(
                    "Z",
                    "+00:00",
                )
            )

            observation_time = (
                datetime.fromisoformat(
                    normalized_time
                )
            )

            if observation_time.tzinfo is None:
                observation_time = (
                    observation_time.replace(
                        tzinfo=timezone.utc
                    )
                )
            else:
                observation_time = (
                    observation_time.astimezone(
                        timezone.utc
                    )
                )

        except ValueError:
            return jsonify(
                {
                    "error": (
                        "Invalid observation_time. "
                        "Use ISO-8601 format."
                    )
                }
            ), 400

    try:
        context = get_earth_context(
            observation_time=observation_time,
        )

    except ValueError as exc:
        return jsonify(
            {
                "error": str(exc),
            }
        ), 400

    earth = context["object"]

    return jsonify(
        {
            "status": "success",
            "data": {
                "object": celestial_object_to_dict(
                    earth
                ),
                "scientific_data": scientific_data_to_dict(
                    context["scientific_data"]
                ),
                "ancestors": [
                    celestial_object_to_dict(
                        ancestor
                    )
                    for ancestor in context["ancestors"]
                ],
                "children": [
                    celestial_object_to_dict(
                        child
                    )
                    for child in context["children"]
                ],
            },
        }
    )


@api.get("/space-weather")
def space_weather():
    try:
        scientific_data = get_space_weather_data()
    except Exception as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 502

    return jsonify(
        {
            "status": "success",
            "data": space_weather_data_to_dict(
                scientific_data
            ),
        }
    )


@api.get("/planets")
def planets():

    return jsonify(
        {
            "count": len(PLANETS),
            "planets": [
                {
                    "name": planet.name,
                    "skyfield_object": (
                        planet.skyfield_name
                    ),
                }
                for planet in PLANETS
            ],
        }
    )


@api.get("/planets/<planet_name>")
def planet_detail(planet_name):

    planet_name = (
        planet_name
        .strip()
        .lower()
    )

    if planet_name not in PLANET_LOOKUP:

        return jsonify(
            {
                "error": (
                    "Invalid planetary body."
                )
            }
        ), 404

    planet = PLANET_LOOKUP[
        planet_name
    ]

    return jsonify(
        {
            "name": planet.name,
            "skyfield_object": (
                planet.skyfield_name
            ),
        }
    )


@api.get("/planets/<planet_name>/trajectory")
def planetary_trajectory(planet_name):

    planet_name = (
        planet_name
        .strip()
        .lower()
    )

    if planet_name not in PLANET_LOOKUP:

        return jsonify(
            {
                "error": (
                    "Invalid planetary body."
                )
            }
        ), 404

    try:

        days = int(
            request.args.get(
                "days",
                "365",
            )
        )

        samples = int(
            request.args.get(
                "samples",
                "181",
            )
        )

    except ValueError:

        return jsonify(
            {
                "error": (
                    "days and samples must be integers."
                )
            }
        ), 400

    if days < 1:

        return jsonify(
            {
                "error": (
                    "days must be at least 1."
                )
            }
        ), 400

    if samples < 2:

        return jsonify(
            {
                "error": (
                    "samples must be at least 2."
                )
            }
        ), 400

    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time"
        )
    )

    if observation_time_text:

        try:

            observation_time = (
                datetime.fromisoformat(
                    observation_time_text.replace(
                        "Z",
                        "+00:00",
                    )
                )
            )

            if observation_time.tzinfo is None:

                observation_time = (
                    observation_time.replace(
                        tzinfo=timezone.utc
                    )
                )

            else:

                observation_time = (
                    observation_time.astimezone(
                        timezone.utc
                    )
                )

        except ValueError:

            return jsonify(
                {
                    "error": (
                        "Invalid observation_time. "
                        "Use ISO 8601 format."
                    )
                }
            ), 400

    try:

        trajectory = (
            calculate_planetary_trajectory(
                planet_name,
                observation_time=observation_time,
                days=days,
                samples=samples,
            )
        )

    except ValueError as exc:

        return jsonify(
            {
                "error": str(exc)
            }
        ), 400

    return jsonify(
        {
            "status": "success",
            "data": {
                "object_id": planet_name,
                "name": PLANET_LOOKUP[
                    planet_name
                ].name,
                "observation_time": (
                    trajectory[0]["date"].isoformat()
                    if trajectory
                    else None
                ),
                "days": days,
                "samples": trajectory,
            },
        }
    )

@api.get("/asteroids/<designation>")
def asteroid_tracking(designation):

    designation = designation.strip()

    if not designation:

        return jsonify(
            {
                "error": (
                    "Asteroid designation "
                    "cannot be empty."
                )
            }
        ), 400

    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time",
            "",
        ).strip()
    )

    if observation_time_text:

        try:

            normalized_time = (
                observation_time_text
                .replace(
                    "Z",
                    "+00:00",
                )
            )

            observation_time = (
                datetime.fromisoformat(
                    normalized_time
                )
            )

            if observation_time.tzinfo is None:

                observation_time = (
                    observation_time.replace(
                        tzinfo=timezone.utc
                    )
                )

            else:

                observation_time = (
                    observation_time.astimezone(
                        timezone.utc
                    )
                )

        except ValueError:

            return jsonify(
                {
                    "error": (
                        "Invalid observation_time. "
                        "Use ISO-8601 format, for example "
                        "2026-10-22T00:00:00Z."
                    )
                }
            ), 400

    try:

        result = track_asteroid(
            designation,
            observation_time=observation_time,
        )

        include_trajectory = (
            request.args.get(
                "include_trajectory",
                "false",
            ).strip().lower()
            == "true"
        )

        if include_trajectory:

            result["trajectory"] = (
                calculate_asteroid_trajectory(
                    designation,
                    observation_time=observation_time,
                    samples=181,
                )
            )

    except AsteroidNotFoundError:

        return jsonify(
            {
                "error": (
                    "Asteroid was not found."
                )
            }
        ), 404

    except AsteroidDataError:

        return jsonify(
            {
                "error": (
                    "Invalid asteroid data "
                    "returned by the Minor "
                    "Planet Center."
                )
            }
        ), 502

    except AsteroidServiceError:

        return jsonify(
            {
                "error": (
                    "Asteroid data service "
                    "is currently unavailable."
                )
            }
        ), 502

    return jsonify(
        {
            "status": "success",
            "data": result,
        }
    )

@api.get(
    "/asteroids/<designation>/scientific-data"
)
def asteroid_scientific_data(designation):

    designation = designation.strip()

    if not designation:

        return jsonify(
            {
                "error": (
                    "Asteroid designation "
                    "cannot be empty."
                )
            }
        ), 400

    observation_time = None

    observation_time_text = (
        request.args.get(
            "observation_time",
            "",
        ).strip()
    )

    if observation_time_text:

        try:

            normalized_time = (
                observation_time_text
                .replace(
                    "Z",
                    "+00:00",
                )
            )

            observation_time = (
                datetime.fromisoformat(
                    normalized_time
                )
            )

            if observation_time.tzinfo is None:

                observation_time = (
                    observation_time.replace(
                        tzinfo=timezone.utc
                    )
                )

            else:

                observation_time = (
                    observation_time.astimezone(
                        timezone.utc
                    )
                )

        except ValueError:

            return jsonify(
                {
                    "error": (
                        "Invalid observation_time. "
                        "Use ISO-8601 format, for example "
                        "2026-10-22T00:00:00Z."
                    )
                }
            ), 400

    try:

        scientific_data = (
            get_asteroid_scientific_data(
                designation,
                observation_time=observation_time,
            )
        )

    except AsteroidNotFoundError:

        return jsonify(
            {
                "error": (
                    "Asteroid was not found."
                )
            }
        ), 404

    except AsteroidDataError:

        return jsonify(
            {
                "error": (
                    "Invalid asteroid data "
                    "returned by the Minor "
                    "Planet Center."
                )
            }
        ), 502

    except AsteroidServiceError:

        return jsonify(
            {
                "error": (
                    "Asteroid data service "
                    "is currently unavailable."
                )
            }
        ), 502

    except ValueError as exc:

        return jsonify(
            {
                "error": str(exc)
            }
        ), 400

    return jsonify(
        {
            "status": "success",
            "data": scientific_data_to_dict(
                scientific_data
            ),
        }
    )


@api.get(
    "/asteroids/<designation>/close-approaches"
)
def asteroid_close_approaches(designation):

    designation = designation.strip()

    if not designation:

        return jsonify(
            {
                "error": (
                    "Asteroid designation "
                    "cannot be empty."
                )
            }
        ), 400

    date_min = (
        request.args.get(
            "date-min",
            "",
        ).strip()
        or None
    )

    date_max = (
        request.args.get(
            "date-max",
            "",
        ).strip()
        or None
    )

    try:

        results = get_close_approach_data(
            designation,
            date_min=date_min,
            date_max=date_max,
        )

    except ValueError as exc:

        return jsonify(
            {
                "error": str(exc)
            }
        ), 400

    except CloseApproachServiceError as exc:

        current_app.logger.warning(
            "CNEOS close-approach service unavailable: %s",
            exc,
        )

        return jsonify(
            {
                "error": str(exc)
            }
        ), 502

    return jsonify(
        {
            "status": "success",
            "data": [
                close_approach_to_dict(
                    result
                )
                for result in results
            ],
        }
    )


@api.get(
    "/spacecraft/<norad_id>/scientific-data"
)
def spacecraft_scientific_data(norad_id):

    norad_id = norad_id.strip()

    if not norad_id.isdigit():

        return jsonify(
            {
                "error": (
                    "NORAD ID must be numeric."
                )
            }
        ), 400

    try:

        scientific_data = (
            get_spacecraft_scientific_data(
                norad_id
            )
        )

    except SpacecraftNotFoundError:

        return jsonify(
            {
                "error": (
                    "Spacecraft was not found."
                )
            }
        ), 404

    except SpacecraftServiceError:

        return jsonify(
            {
                "error": (
                    "Spacecraft data service "
                    "is currently unavailable."
                )
            }
        ), 502

    except ValueError as exc:

        return jsonify(
            {
                "error": str(exc)
            }
        ), 400

    return jsonify(
        {
            "status": "success",
            "data": scientific_data_to_dict(
                scientific_data
            ),
        }
    )


@api.get("/spacecraft/<norad_id>")
def spacecraft_tracking(norad_id):

    norad_id = norad_id.strip()

    if not norad_id.isdigit():

        return jsonify(
            {
                "error": (
                    "NORAD ID must be numeric."
                )
            }
        ), 400

    try:

        result = track_spacecraft_by_norad(
            norad_id
        )

    except SpacecraftNotFoundError:

        return jsonify(
            {
                "error": (
                    "Spacecraft was not found."
                )
            }
        ), 404

    except SpacecraftServiceError:

        return jsonify(
            {
                "error": (
                    "Spacecraft data service "
                    "is currently unavailable."
                )
            }
        ), 502

    return jsonify(
        {
            "status": "success",
            "data": result,
        }
    )


@api.get("/overview")
def overview():

    now, results = (
        generate_solar_system_overview()
    )

    return jsonify(
        {
            "calculation_time": (
                now.utc_strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
            ),
            "count": len(results),
            "objects": [
                {
                    "name": result["name"],
                    "distance_from_sun_km": (
                        result[
                            "distance_from_sun"
                        ]
                    ),
                    "distance_from_earth_km": (
                        result[
                            "distance_from_earth"
                        ]
                    ),
                }
                for result in results
            ],
        }
    )


@api.post("/analysis")
def analysis():

    data = request.get_json(
        silent=True
    ) or {}

    reference_name = (
        str(
            data.get(
                "reference",
                "",
            )
        )
        .strip()
        .lower()
    )

    target_name = (
        str(
            data.get(
                "target",
                "",
            )
        )
        .strip()
        .lower()
    )

    if reference_name not in PLANET_LOOKUP:

        return jsonify(
            {
                "error": (
                    "Invalid reference body."
                )
            }
        ), 400

    if target_name not in PLANET_LOOKUP:

        return jsonify(
            {
                "error": (
                    "Invalid target body."
                )
            }
        ), 400

    if reference_name == target_name:

        return jsonify(
            {
                "error": (
                    "Reference body and target body "
                    "cannot be the same."
                )
            }
        ), 400

    start_date_text = (
        str(
            data.get(
                "start_date",
                "",
            )
        )
        .strip()
    )

    try:

        start_date = datetime.strptime(
            start_date_text,
            "%Y-%m-%d",
        ).replace(
            tzinfo=timezone.utc
        )

    except ValueError:

        return jsonify(
            {
                "error": (
                    "Invalid start_date. "
                    "Use YYYY-MM-DD."
                )
            }
        ), 400

    try:

        months = int(
            data.get(
                "months",
                12,
            )
        )

        interval_days = int(
            data.get(
                "interval_days",
                30,
            )
        )

    except (TypeError, ValueError):

        return jsonify(
            {
                "error": (
                    "months and interval_days "
                    "must be integers."
                )
            }
        ), 400

    try:

        results = analyze_body_distance(
            reference_body_name=(
                PLANET_LOOKUP[
                    reference_name
                ].skyfield_name
            ),
            target_body_name=(
                PLANET_LOOKUP[
                    target_name
                ].skyfield_name
            ),
            start_date=start_date,
            months=months,
            interval_days=interval_days,
        )

    except ValueError as exc:

        return jsonify(
            {
                "error": str(exc),
            }
        ), 400

    return jsonify(
        {
            "reference": (
                PLANET_LOOKUP[
                    reference_name
                ].name
            ),
            "target": (
                PLANET_LOOKUP[
                    target_name
                ].name
            ),
            "start_date": (
                start_date.strftime(
                    "%Y-%m-%d"
                )
            ),
            "months": months,
            "interval_days": interval_days,
            "count": len(results),
            "results": [
                {
                    "date": (
                        result["date"].strftime(
                            "%Y-%m-%d"
                        )
                    ),
                    "distance_km": (
                        result[
                            "distance_km"
                        ]
                    ),
                    "relative_velocity_km_s": (
                        result[
                            "relative_velocity_km_s"
                        ]
                    ),
                }
                for result in results
            ],
        }
    )

@api.get("/monitoring/status")
def monitoring_status():
    """Return the persisted health of monitoring sources."""

    try:
        return jsonify(
            {
                "status": "success",
                "data": get_monitoring_status(),
            }
        )
    except Exception:
        return jsonify(
            {
                "status": "error",
                "error": "Monitoring status retrieval failed.",
            }
        ), 500

def _monitoring_limit():
    value = request.args.get("limit", "100")

    try:
        limit = int(value)
    except ValueError:
        raise ValueError("limit must be an integer.")

    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500.")

    return limit


@api.get("/monitoring/events")
def monitoring_events():
    """Return persisted monitoring events."""

    try:
        limit = _monitoring_limit()

        events = list_monitoring_events(
            limit=limit,
            event_type=request.args.get("event_type"),
            severity=request.args.get("severity"),
            status=request.args.get("status"),
            source=request.args.get("source"),
        )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "count": len(events),
                    "events": events,
                },
            }
        )

    except ValueError as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 400

    except Exception:
        return jsonify(
            {
                "status": "error",
                "error": "Monitoring event retrieval failed.",
            }
        ), 500


@api.get("/monitoring/alerts")
def monitoring_alerts():
    """Return persisted monitoring alerts."""

    try:
        limit = _monitoring_limit()

        acknowledged_arg = request.args.get(
            "acknowledged"
        )

        acknowledged = None

        if acknowledged_arg is not None:
            normalized = acknowledged_arg.strip().lower()

            if normalized == "true":
                acknowledged = True
            elif normalized == "false":
                acknowledged = False
            else:
                raise ValueError(
                    "acknowledged must be true or false."
                )

        alerts = list_monitoring_alerts(
            limit=limit,
            acknowledged=acknowledged,
        )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "count": len(alerts),
                    "alerts": alerts,
                },
            }
        )

    except ValueError as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 400

    except Exception:
        return jsonify(
            {
                "status": "error",
                "error": "Monitoring alert retrieval failed.",
            }
        ), 500


@api.post(
    "/monitoring/alerts/<alert_id>/acknowledge"
)
def acknowledge_monitoring_alert_api(alert_id):
    """Acknowledge a monitoring alert."""

    try:
        acknowledged = acknowledge_monitoring_alert(
            alert_id
        )

        if not acknowledged:
            return jsonify(
                {
                    "status": "error",
                    "error": "Monitoring alert not found.",
                }
            ), 404

        return jsonify(
            {
                "status": "success",
                "data": {
                    "alert_id": alert_id,
                    "acknowledged": True,
                },
            }
        )

    except Exception:
        return jsonify(
            {
                "status": "error",
                "error": (
                    "Monitoring alert acknowledgement failed."
                ),
            }
        ), 500

@api.post("/ai/query")
def ai_query():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify(
            {
                "status": "error",
                "error": "JSON object is required.",
            }
        ), 400

    message = payload.get("message")

    if message is not None:
        conversation_id = payload.get(
            "conversation_id"
        )

        if (
            not isinstance(conversation_id, str)
            or not conversation_id.strip()
        ):
            return jsonify(
                {
                    "status": "error",
                    "error": (
                        "conversation_id is required "
                        "for assistant messages."
                    ),
                }
            ), 400

        object_id = payload.get("object_id")

        if object_id is not None and not isinstance(
            object_id,
            str,
        ):
            return jsonify(
                {
                    "status": "error",
                    "error": "object_id must be a string.",
                }
            ), 400

        capability_ids = payload.get(
            "capability_ids",
            (),
        )

        if not isinstance(
            capability_ids,
            (list, tuple),
        ):
            return jsonify(
                {
                    "status": "error",
                    "error": "capability_ids must be a list.",
                }
            ), 400

        messages = payload.get(
            "messages",
            (),
        )

        if not isinstance(
            messages,
            (list, tuple),
        ):
            return jsonify(
                {
                    "status": "error",
                    "error": "messages must be a list.",
                }
            ), 400

        conversation_messages = []

        for item in messages:
            if not isinstance(item, dict):
                return jsonify(
                    {
                        "status": "error",
                        "error": (
                            "conversation messages require "
                            "role and content."
                        ),
                    }
                ), 400

            role = item.get("role")
            content = item.get("content")

            if (
                not isinstance(role, str)
                or not role.strip()
                or not isinstance(content, str)
                or not content.strip()
            ):
                return jsonify(
                    {
                        "status": "error",
                        "error": (
                            "conversation messages require "
                            "role and content."
                        ),
                    }
                ), 400

            role = role.strip().lower()

            if role not in (
                "user",
                "assistant",
            ):
                return jsonify(
                    {
                        "status": "error",
                        "error": (
                            "conversation message role "
                            "must be user or assistant."
                        ),
                    }
                ), 400

            message_object_id = item.get(
                "object_id"
            )

            if (
                message_object_id is not None
                and not isinstance(
                    message_object_id,
                    str,
                )
            ):
                return jsonify(
                    {
                        "status": "error",
                        "error": (
                            "conversation message "
                            "object_id must be a string."
                        ),
                    }
                ), 400

            metadata = item.get("metadata")

            if (
                metadata is not None
                and not isinstance(metadata, dict)
            ):
                return jsonify(
                    {
                        "status": "error",
                        "error": (
                            "conversation message "
                            "metadata must be an object."
                        ),
                    }
                ), 400

            conversation_messages.append(
                AssistantMessage(
                    role=role,
                    content=content.strip(),
                    object_id=(
                        message_object_id.strip().lower()
                        if isinstance(
                            message_object_id,
                            str,
                        )
                        and message_object_id.strip()
                        else None
                    ),
                    metadata=metadata,
                )
            )

        observation_time = payload.get(
            "observation_time"
        )
        parameters = payload.get("parameters")

        if (
            parameters is not None
            and not isinstance(parameters, dict)
        ):
            return jsonify(
                {
                    "status": "error",
                    "error": (
                        "parameters must be an object."
                    ),
                }
            ), 400

        try:
            conversation = AIConversation(
                conversation_id=conversation_id.strip(),
                messages=tuple(
                    conversation_messages
                ),
                object_id=(
                    object_id.strip().lower()
                    if isinstance(object_id, str)
                    and object_id.strip()
                    else None
                ),
            )

            language_provider = create_language_provider()

            updated_conversation, result = (
                process_assistant_message(
                    conversation,
                    message,
                    object_id=object_id,
                    observation_time=observation_time,
                    capability_ids=tuple(
                        capability_ids
                    ),
                    parameters=parameters,
                    language_provider=language_provider,
                )
            )

            return jsonify(
                {
                    "status": "success",
                    "data": {
                        "conversation_id": (
                            updated_conversation
                            .conversation_id
                        ),
                        "message": message.strip(),
                        "question": result.question,
                        "object_id": result.object_id,
                        "answer": result.answer,
                        "capabilities": list(
                            result.capabilities
                        ),
                        "observation_time": (
                            result.observation_time
                        ),
                        "provenance": [
                            {
                                "name": source.name,
                                "provider": source.provider,
                                "url": source.url,
                                "dataset": source.dataset,
                                "version": source.version,
                                "upstream_source": source.upstream_source,
                            }
                            for source in result.provenance
                        ],
                        "uncertainties": list(
                            result.uncertainties
                        ),
                        "messages": [
                            {
                                "role": item.role,
                                "content": item.content,
                                "object_id": item.object_id,
                            }
                            for item
                            in updated_conversation.messages
                        ],
                    },
                }
            )

        except ValueError as exc:
            return jsonify(
                {
                    "status": "error",
                    "error": str(exc),
                }
            ), 400

        except Exception as exc:
            return jsonify(
                {
                    "status": "error",
                    "error": (
                        "AI assistant processing failed: "
                        + type(exc).__name__
                        + ": "
                        + str(exc)
                    ),
                }
            ), 500

    question = payload.get("question")
    object_id = payload.get("object_id")

    if not isinstance(question, str) or not question.strip():
        return jsonify(
            {
                "status": "error",
                "error": "question is required.",
            }
        ), 400

    if object_id is not None and (
        not isinstance(object_id, str) or not object_id.strip()
    ):
        return jsonify(
            {
                "status": "error",
                "error": "object_id must be a non-empty string when provided.",
            }
        ), 400

    capability_ids = payload.get("capability_ids", ())

    if not isinstance(capability_ids, (list, tuple)):
        return jsonify(
            {
                "status": "error",
                "error": "capability_ids must be a list.",
            }
        ), 400

    observation_time = payload.get("observation_time")
    parameters = payload.get("parameters")

    if parameters is not None and not isinstance(parameters, dict):
        return jsonify(
            {
                "status": "error",
                "error": "parameters must be an object.",
            }
        ), 400

    try:
        orchestration_request = AIOrchestrationRequest(
            question=question.strip(),
            object_id=object_id.strip() if object_id is not None else None,
            capability_ids=tuple(capability_ids),
            observation_time=observation_time,
            parameters=parameters,
        )

        language_provider = create_language_provider()

        result = orchestrate_ai_request(
            orchestration_request,
            language_provider=language_provider,
        )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "question": result.question,
                    "object_id": result.object_id,
                    "answer": result.answer,
                    "capabilities": list(result.capabilities),
                    "results": [
                        _capability_result_to_dict(
                            capability_result
                        )
                        for capability_result
                        in result.results
                    ],
                    "facts": _fact_set_to_dict(
                        result.facts
                    ),
                    "interpretations": _interpretation_set_to_dict(
                        result.interpretations
                    ),
                    "observation_time": (
                        _observation_time_to_string(
                            result.observation_time
                        )
                    ),
                    "provenance": [
                        {
                            "name": source.name,
                            "provider": source.provider,
                            "url": source.url,
                            "dataset": source.dataset,
                            "version": source.version,
                            "upstream_source": source.upstream_source,
                        }
                        for source in result.provenance
                    ],
                    "uncertainties": list(
                        result.uncertainties
                    ),
                },
            }
        )

    except ValueError as exc:
        return jsonify(
            {
                "status": "error",
                "error": str(exc),
            }
        ), 400

    except Exception:
        return jsonify(
            {
                "status": "error",
                "error": "AI query processing failed.",
            }
        ), 500
