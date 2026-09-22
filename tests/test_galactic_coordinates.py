from astrosphere.models.galactic import (
    GalacticCoordinate,
)
from astrosphere.models.galactic_serialization import (
    galactic_coordinate_to_dict,
)


def test_galactic_coordinate_creation():
    coordinate = GalacticCoordinate(
        longitude_deg=123.45,
        latitude_deg=-12.34,
        distance_pc=100.0,
    )

    assert coordinate.longitude_deg == 123.45
    assert coordinate.latitude_deg == -12.34
    assert coordinate.distance_pc == 100.0
    assert coordinate.frame == "galactic"


def test_galactic_coordinate_supports_missing_distance():
    coordinate = GalacticCoordinate(
        longitude_deg=10.0,
        latitude_deg=20.0,
    )

    assert coordinate.longitude_deg == 10.0
    assert coordinate.latitude_deg == 20.0
    assert coordinate.distance_pc is None
    assert coordinate.frame == "galactic"


def test_galactic_coordinate_serialization():
    coordinate = GalacticCoordinate(
        longitude_deg=123.45,
        latitude_deg=-12.34,
        distance_pc=100.0,
    )

    result = galactic_coordinate_to_dict(
        coordinate
    )

    assert result == {
        "longitude_deg": 123.45,
        "latitude_deg": -12.34,
        "distance_pc": 100.0,
        "frame": "galactic",
        "origin": "sun",
        "source": None,
    }
from astrosphere.models.galactic import (
    GalacticCoordinate,
)
from astrosphere.models.scientific import (
    DataSource,
)


def test_galactic_coordinate_supports_data_source():
    source = DataSource(
        name="Test Galactic Dataset",
        provider="Test Provider",
        dataset="test-galactic",
    )

    coordinate = GalacticCoordinate(
        longitude_deg=123.45,
        latitude_deg=-12.34,
        distance_pc=100.0,
        source=source,
    )

    assert coordinate.source == source
    assert coordinate.source.name == "Test Galactic Dataset"
    assert coordinate.source.provider == "Test Provider"
    assert coordinate.source.dataset == "test-galactic"

def test_galactic_coordinate_serialization_includes_data_source():
    source = DataSource(
        name="Test Galactic Dataset",
        provider="Test Provider",
        dataset="test-galactic",
        version="1.0",
    )

    coordinate = GalacticCoordinate(
        longitude_deg=123.45,
        latitude_deg=-12.34,
        distance_pc=100.0,
        source=source,
    )

    result = galactic_coordinate_to_dict(
        coordinate
    )

    assert result["source"] == {
        "name": "Test Galactic Dataset",
        "provider": "Test Provider",
        "url": None,
        "dataset": "test-galactic",
        "version": "1.0",
        "upstream_source": None,
    }

def test_galactic_coordinate_has_explicit_origin():
    coordinate = GalacticCoordinate(
        longitude_deg=123.45,
        latitude_deg=-12.34,
        distance_pc=100.0,
    )

    assert coordinate.origin == "sun"
