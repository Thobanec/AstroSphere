from datetime import datetime, timezone

from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)


def test_analyze_body_distance_returns_results():

    results = analyze_body_distance(
        "earth",
        "jupiter barycenter",
        datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        months=3,
        interval_days=7,
    )

    assert results

    assert len(results) == 14


def test_orbital_analysis_result_structure():

    results = analyze_body_distance(
        "earth",
        "jupiter barycenter",
        datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        months=3,
        interval_days=7,
    )

    first_result = results[0]

    assert "date" in first_result

    assert "distance_km" in first_result

    assert "relative_velocity_km_s" in first_result


def test_orbital_analysis_values_are_positive():

    results = analyze_body_distance(
        "earth",
        "jupiter barycenter",
        datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        months=3,
        interval_days=7,
    )

    for result in results:

        assert result["distance_km"] > 0

        assert (
            result["relative_velocity_km_s"]
            >= 0
        )


def test_orbital_analysis_dates_are_ordered():

    results = analyze_body_distance(
        "earth",
        "jupiter barycenter",
        datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        months=3,
        interval_days=7,
    )

    dates = [
        result["date"]
        for result in results
    ]

    assert dates == sorted(dates)