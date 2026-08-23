from datetime import datetime, timezone

from flask import Flask, render_template, request

from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)

from astrosphere.astronomy.calculations import (
    calculate_distance_km,
    calculate_relative_velocity_km_s,
    get_current_time,
    load_solar_system,
)

from astrosphere.astronomy.planets import (
    PLANET_LOOKUP,
)

from astrosphere.analysis_config import (
    AnalysisConfig,
)

from astrosphere.overview import (
    generate_solar_system_overview,
)

app = Flask(__name__)


@app.route("/")
def index():

    return render_template(
        "index.html",
        planets=PLANET_LOOKUP,
    )


@app.route("/overview")
def overview():

    now, results = (
        generate_solar_system_overview()
    )

    return render_template(
        "overview.html",
        now=now,
        results=results,
    )

@app.route("/planet/<planet_name>")
def planet_detail(planet_name):

    planet_name = (
        planet_name
        .strip()
        .lower()
    )

    if planet_name not in PLANET_LOOKUP:

        return render_template(
            "error.html",
            message="Invalid planetary body.",
        )

    planet = PLANET_LOOKUP[
        planet_name
    ]

    solar_system = load_solar_system()

    now = get_current_time()

    sun = solar_system["sun"]
    earth = solar_system["earth"]

    body = solar_system[
        planet.skyfield_name
    ]

    sun_position = sun.at(now)

    earth_position = earth.at(now)

    body_position = body.at(now)


    distance_from_sun = calculate_distance_km(
        body_position,
        sun_position,
    )


    distance_from_earth = calculate_distance_km(
        body_position,
        earth_position,
    )


    velocity_relative_to_earth = (
        calculate_relative_velocity_km_s(
            earth_position,
            body_position,
        )
    )


    return render_template(
        "planet.html",

        planet=planet,

        now=now,

        distance_from_sun=distance_from_sun,

        distance_from_earth=distance_from_earth,

        velocity_relative_to_earth=(
            velocity_relative_to_earth
        ),
    )


@app.route("/analyze", methods=["POST"])
def analyze():

    reference_name = request.form.get(
        "reference",
        ""
    ).strip().lower()

    target_name = request.form.get(
        "target",
        ""
    ).strip().lower()

    start_date_text = request.form.get(
        "start_date",
        ""
    ).strip()

    months_text = request.form.get(
        "period",
        ""
    ).strip()

    interval_text = request.form.get(
        "interval",
        ""
    ).strip()


    # ---------------------------------------------------------
    # VALIDATE REFERENCE BODY
    # ---------------------------------------------------------

    if reference_name not in PLANET_LOOKUP:

        return render_template(
            "error.html",
            message="Invalid reference body.",
        )


    # ---------------------------------------------------------
    # VALIDATE TARGET BODY
    # ---------------------------------------------------------

    if target_name not in PLANET_LOOKUP:

        return render_template(
            "error.html",
            message="Invalid target body.",
        )


    # ---------------------------------------------------------
    # VALIDATE REFERENCE / TARGET
    # ---------------------------------------------------------

    if reference_name == target_name:

        return render_template(
            "error.html",
            message=(
                "Reference body and target body "
                "cannot be the same."
            ),
        )


    # ---------------------------------------------------------
    # PARSE START DATE
    # ---------------------------------------------------------

    try:

        analysis_date = datetime.strptime(
            start_date_text,
            "%Y-%m-%d",
        ).replace(
            tzinfo=timezone.utc
        )

    except ValueError:

        return render_template(
            "error.html",
            message=(
                "Invalid date. "
                "Please provide a valid date."
            ),
        )


    # ---------------------------------------------------------
    # PARSE ANALYSIS PARAMETERS
    # ---------------------------------------------------------

    try:

        months = int(months_text)

        interval_days = int(interval_text)

    except ValueError:

        return render_template(
            "error.html",
            message="Invalid analysis parameters.",
        )


    # ---------------------------------------------------------
    # GET PLANETARY OBJECTS
    # ---------------------------------------------------------

    reference_body = PLANET_LOOKUP[
        reference_name
    ]

    target_body = PLANET_LOOKUP[
        target_name
    ]


    # ---------------------------------------------------------
    # CREATE ANALYSIS CONFIGURATION
    # ---------------------------------------------------------

    config = AnalysisConfig(
        start_date=analysis_date,
        months=months,
        interval_days=interval_days,
        reference_body=reference_body,
    )


    # ---------------------------------------------------------
    # RUN ORBITAL ANALYSIS
    # ---------------------------------------------------------

    try:

        results = analyze_body_distance(
            reference_body_name=(
                config.reference_body.skyfield_name
            ),
            target_body_name=(
                target_body.skyfield_name
            ),
            start_date=config.start_date,
            months=config.months,
            interval_days=config.interval_days,
        )

    except ValueError as error:

        return render_template(
            "error.html",
            message=str(error),
        )


    # ---------------------------------------------------------
    # CHECK RESULTS
    # ---------------------------------------------------------

    if not results:

        return render_template(
            "error.html",
            message="No orbital data was returned.",
        )


    # ---------------------------------------------------------
    # CLOSEST / FARTHEST
    # ---------------------------------------------------------

    closest = min(
        results,
        key=lambda result: result["distance_km"],
    )

    farthest = max(
        results,
        key=lambda result: result["distance_km"],
    )


    # ---------------------------------------------------------
    # BASIC DISTANCE STATISTICS
    # ---------------------------------------------------------

    initial_km = results[0]["distance_km"]

    final_km = results[-1]["distance_km"]

    minimum_km = closest["distance_km"]

    maximum_km = farthest["distance_km"]


    variation_km = (
        maximum_km - minimum_km
    )


    average_km = sum(
        result["distance_km"]
        for result in results
    ) / len(results)


    # ---------------------------------------------------------
    # DISTANCE CHANGE
    # ---------------------------------------------------------

    distance_change_km = (
        final_km - initial_km
    )


    # ---------------------------------------------------------
    # PERCENTAGE CHANGE
    # ---------------------------------------------------------

    if initial_km != 0:

        percentage_change = (
            distance_change_km
            / initial_km
        ) * 100

    else:

        percentage_change = 0.0


       # ---------------------------------------------------------
    # DETERMINE TREND
    # ---------------------------------------------------------

    if distance_change_km < 0:

        trend = "Getting closer"

    elif distance_change_km > 0:

        trend = "Getting farther apart"

    else:

        trend = "No overall change"


    # ---------------------------------------------------------
    # RELATIVE VELOCITY STATISTICS
    # ---------------------------------------------------------

    initial_velocity_km_s = (
        results[0]["relative_velocity_km_s"]
    )

    final_velocity_km_s = (
        results[-1]["relative_velocity_km_s"]
    )

    minimum_velocity_km_s = min(
        result["relative_velocity_km_s"]
        for result in results
    )

    maximum_velocity_km_s = max(
        result["relative_velocity_km_s"]
        for result in results
    )

    average_velocity_km_s = sum(
        result["relative_velocity_km_s"]
        for result in results
    ) / len(results)

    velocity_change_km_s = (
        final_velocity_km_s
        - initial_velocity_km_s
    )

    if initial_velocity_km_s != 0:

        velocity_percentage_change = (
            velocity_change_km_s
            / initial_velocity_km_s
        ) * 100

    else:

        velocity_percentage_change = 0.0


    if velocity_change_km_s < 0:

        velocity_trend = "Slowing down"

    elif velocity_change_km_s > 0:

        velocity_trend = "Speeding up"

    else:

        velocity_trend = "No overall change"


    # ---------------------------------------------------------
    # PREPARE CHART DATA
    # ---------------------------------------------------------

    chart_dates = [
        result["date"].strftime("%Y-%m-%d")
        for result in results
    ]

    chart_distances = [
        result["distance_km"] / 1_000_000
        for result in results
    ]

    chart_velocities = [
        result["relative_velocity_km_s"]
        for result in results
    ]


    # ---------------------------------------------------------
    # RENDER RESULTS PAGE
    # ---------------------------------------------------------

    return render_template(
        "results.html",

        reference_body=reference_body,
        target_body=target_body,

        config=config,

        results=results,

        closest=closest,
        farthest=farthest,

        initial_km=initial_km,
        final_km=final_km,

        minimum_km=minimum_km,
        maximum_km=maximum_km,

        variation_km=variation_km,
        average_km=average_km,

        distance_change_km=distance_change_km,
        percentage_change=percentage_change,

        trend=trend,

        initial_velocity_km_s=initial_velocity_km_s,
        final_velocity_km_s=final_velocity_km_s,

        minimum_velocity_km_s=minimum_velocity_km_s,
        maximum_velocity_km_s=maximum_velocity_km_s,

        average_velocity_km_s=average_velocity_km_s,

        velocity_change_km_s=velocity_change_km_s,
        velocity_percentage_change=velocity_percentage_change,

        velocity_trend=velocity_trend,

        chart_dates=chart_dates,
        chart_distances=chart_distances,
        chart_velocities=chart_velocities,
    )
 
if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )