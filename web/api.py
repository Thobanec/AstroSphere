from flask import (
    Blueprint,
    jsonify,
    request,
)

from datetime import datetime, timezone

from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)

from astrosphere.astronomy.planets import (
    PLANET_LOOKUP,
)

from astrosphere.astronomy.planets import (
    PLANET_LOOKUP,
    PLANETS,
)

from astrosphere.overview import (
    generate_solar_system_overview,
)

from astrosphere.astronomy.planets import PLANETS


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api/v1",
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