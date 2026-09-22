from astrosphere.models.stellar_scientific_catalog import (
    get_stellar_scientific_properties,
)


def test_stellar_scientific_catalog_contains_initial_stars():
    expected = {
        "sun",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    }

    actual = {
        object_id
        for object_id in expected
        if get_stellar_scientific_properties(object_id)
        is not None
    }

    assert actual == expected


def test_sun_has_scientific_properties():
    data = get_stellar_scientific_properties("sun")

    assert data is not None
    assert data.source.name == "NASA Sun Fact Sheet"
    assert data.physical_properties["mass_kg"] == 1.9884e30
    assert data.physical_properties["mean_radius_km"] == 695700.0
    assert data.physical_properties["effective_temperature_k"] == 5772.0
    assert data.stellar_properties["spectral_type"] == "G2 V"


def test_sirius_has_scientific_properties():
    data = get_stellar_scientific_properties("sirius")

    assert data is not None
    assert data.source.provider == "NASA Hubble Space Telescope"
    assert data.physical_properties["mass_solar"] == 2.0
    assert data.physical_properties["distance_pc"] == 2.6
    assert data.stellar_properties["system_type"] == "binary"


def test_proxima_centauri_has_scientific_properties():
    data = get_stellar_scientific_properties(
        "proxima-centauri"
    )

    assert data is not None
    assert data.physical_properties["mass_solar"] == 0.125
    assert data.physical_properties["distance_light_years"] == 4.24
    assert data.stellar_properties["spectral_type"] == "M5.5Ve"


def test_betelgeuse_has_scientific_properties():
    data = get_stellar_scientific_properties(
        "betelgeuse"
    )

    assert data is not None
    assert data.physical_properties["mass_solar"] == 15.0
    assert data.physical_properties["radius_solar"] == 700.0
    assert data.stellar_properties["stellar_class"] == (
        "red supergiant"
    )


def test_vega_has_scientific_properties():
    data = get_stellar_scientific_properties("vega")

    assert data is not None
    assert data.physical_properties["mass_solar"] == 2.5
    assert data.physical_properties["luminosity_solar"] == 60.0
    assert data.physical_properties["distance_pc"] == 8.1
    assert data.stellar_properties["spectral_type"] == "A0Va"


def test_stellar_scientific_catalog_lookup_is_case_insensitive():
    data = get_stellar_scientific_properties("SIRIUS")

    assert data is not None
    assert data.object_id == "sirius"


def test_stellar_scientific_catalog_unknown_returns_none():
    data = get_stellar_scientific_properties(
        "unknown-star"
    )

    assert data is None
