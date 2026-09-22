from astrosphere.scientific.service import (
    get_scientific_data,
)


def test_get_scientific_data_for_sirius():
    data = get_scientific_data("sirius")

    assert data.object_id == "sirius"
    assert data.observation is None
    assert data.position is None
    assert data.velocity is None

    assert data.physical_properties["mass_solar"] == 2.0
    assert data.physical_properties["diameter_km"] == 2.4e6
    assert data.stellar_properties["system_type"] == "binary"

    assert data.physical_properties_source is not None
    assert (
        data.physical_properties_source.name
        == "NASA Hubble Sirius Observation"
    )

    assert data.stellar_properties_source == (
        data.physical_properties_source
    )

    assert data.provenance.sources == (
        data.physical_properties_source,
    )

    assert data.provenance.reference_frames == ()


def test_get_scientific_data_for_other_registered_stars():
    expected = {
        "proxima-centauri": "M5.5Ve",
        "betelgeuse": "red supergiant",
        "vega": "A0Va",
    }

    for object_id, expected_value in expected.items():
        data = get_scientific_data(object_id)

        assert data.object_id == object_id
        assert data.physical_properties
        assert data.stellar_properties

        if object_id == "proxima-centauri":
            assert (
                data.stellar_properties["spectral_type"]
                == expected_value
            )

        elif object_id == "betelgeuse":
            assert (
                data.stellar_properties["stellar_class"]
                == expected_value
            )

        elif object_id == "vega":
            assert (
                data.stellar_properties["spectral_type"]
                == expected_value
            )
