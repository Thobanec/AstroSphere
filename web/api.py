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
from astrosphere.scientific.earth import (
    get_earth_context,
)
from astrosphere.scientific.space_weather import (
    get_space_weather_data,
)
from astrosphere.scientific.service import (
    get_scientific_data,
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


@api.get("/celestial-objects/<object_id>/relationships")
def celestial_object_relationships(object_id):

    from astrosphere.models.celestial_registry import (
        get_ancestors,
        get_celestial_object,
        get_children,
        get_parent_object,
    )

    object_id = object_id.strip().lower()
    obj = get_celestial_object(object_id)

    if obj is None:
        return jsonify(
            {
                "status": "error",
                "error": "Celestial object was not found.",
            }
        ), 404

    parent = get_parent_object(object_id)
    ancestors = get_ancestors(object_id)
    children = get_children(object_id)

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
                    for ancestor in ancestors
                ],
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
