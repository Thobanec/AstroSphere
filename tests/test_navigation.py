from astrosphere.navigation import (
    get_celestial_object_url,
)


def test_milky_way_uses_galaxy_explorer():
    assert (
        get_celestial_object_url("milky-way")
        == "/galaxy"
    )


def test_solar_system_uses_solar_system_explorer():
    assert (
        get_celestial_object_url("solar-system")
        == "/solar-system"
    )


def test_planet_uses_canonical_celestial_explorer():
    assert (
        get_celestial_object_url("earth")
        == "/celestial/earth"
    )


def test_stellar_object_uses_canonical_celestial_explorer():
    assert (
        get_celestial_object_url("sirius")
        == "/celestial/sirius"
    )


def test_special_id_uses_path_safe_canonical_explorer():
    assert (
        get_celestial_object_url("spacecraft:25544")
        == "/celestial/spacecraft:25544"
    )


def test_unknown_object_has_no_navigation_target():
    assert (
        get_celestial_object_url("not-a-real-object")
        is None
    )


def test_invalid_navigation_input_has_no_target():
    assert get_celestial_object_url(None) is None
    assert get_celestial_object_url("") is None
    assert get_celestial_object_url("   ") is None
