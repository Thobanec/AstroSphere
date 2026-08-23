from math import isclose

from astrosphere.overview import (
    generate_solar_system_overview,
)


def test_generate_solar_system_overview():

    now, results = (
        generate_solar_system_overview()
    )

    assert now is not None

    assert len(results) == 9


def test_overview_contains_expected_planets():

    _, results = (
        generate_solar_system_overview()
    )

    names = [
        result["name"]
        for result in results
    ]

    expected_names = [
        "Mercury",
        "Venus",
        "Earth",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]

    assert names == expected_names


def test_overview_contains_distance_values():

    _, results = (
        generate_solar_system_overview()
    )

    for result in results:

        assert "name" in result

        assert "distance_from_sun" in result

        assert "distance_from_earth" in result

        assert result["distance_from_sun"] > 0

        assert result["distance_from_earth"] >= 0


def test_earth_distance_from_earth_is_zero():

    _, results = (
        generate_solar_system_overview()
    )

    earth = next(
        result
        for result in results
        if result["name"] == "Earth"
    )

    assert isclose(
        earth["distance_from_earth"],
        0.0,
        abs_tol=1e-6,
    )