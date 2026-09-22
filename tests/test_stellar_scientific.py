from astrosphere.models.scientific import DataSource
from astrosphere.models.stellar_scientific import (
    StellarScientificProperties,
)


def test_stellar_scientific_properties_creation():
    source = DataSource(
        name="Test Stellar Dataset",
        provider="Test Provider",
        dataset="test-stellar",
    )

    properties = StellarScientificProperties(
        object_id="sun",
        source=source,
        physical_properties={
            "mass_solar": 1.0,
            "radius_solar": 1.0,
        },
        stellar_properties={
            "spectral_type": "G2V",
        },
    )

    assert properties.object_id == "sun"
    assert properties.source == source
    assert properties.physical_properties["mass_solar"] == 1.0
    assert properties.physical_properties["radius_solar"] == 1.0
    assert properties.stellar_properties["spectral_type"] == "G2V"


def test_stellar_scientific_properties_requires_source():
    source = DataSource(
        name="Test Stellar Dataset",
        provider="Test Provider",
        dataset="test-stellar",
    )

    properties = StellarScientificProperties(
        object_id="sirius",
        source=source,
        physical_properties={},
        stellar_properties={},
    )

    assert properties.source.name == "Test Stellar Dataset"
