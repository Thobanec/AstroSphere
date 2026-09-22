from astrosphere.models.galactic import (
    GalacticCoordinate,
)
from astrosphere.models.galactic_catalog import (
    GalacticCoordinateData,
)
from astrosphere.models.scientific import (
    DataSource,
)


def test_galactic_coordinate_data_creation():
    coordinate = GalacticCoordinate(
        longitude_deg=123.45,
        latitude_deg=-12.34,
        distance_pc=100.0,
    )

    source = DataSource(
        name="Test Galactic Dataset",
        provider="Test Provider",
        dataset="test-galactic",
    )

    data = GalacticCoordinateData(
        object_id="sun",
        source=source,
        coordinate=coordinate,
    )

    assert data.object_id == "sun"
    assert data.source == source
    assert data.coordinate == coordinate

def test_galactic_coordinate_data_lookup_returns_record():
    from astrosphere.models.galactic_catalog import (
        get_galactic_coordinate_data,
    )

    data = get_galactic_coordinate_data("sun")

    assert data is not None
    assert data.object_id == "sun"
    assert data.source is not None
    assert data.coordinate is not None


def test_galactic_coordinate_data_lookup_is_case_insensitive():
    from astrosphere.models.galactic_catalog import (
        get_galactic_coordinate_data,
    )

    data = get_galactic_coordinate_data("SUN")

    assert data is not None
    assert data.object_id == "sun"


def test_galactic_coordinate_data_lookup_returns_none_for_unknown_object():
    from astrosphere.models.galactic_catalog import (
        get_galactic_coordinate_data,
    )

    data = get_galactic_coordinate_data(
        "unknown-object"
    )

    assert data is None

def test_galactic_coordinate_data_has_scientific_source_metadata():
    from astrosphere.models.galactic_catalog import (
        get_galactic_coordinate_data,
    )

    data = get_galactic_coordinate_data("sun")

    assert data is not None
    assert data.object_id == "sun"

    assert data.source.name == (
        "HEASARC Galactic Coordinate System"
    )
    assert data.source.provider == (
        "NASA Goddard Space Flight Center HEASARC"
    )
    assert data.source.dataset == "Galactic Coordinates"
    assert data.source.url == (
        "https://heasarc.gsfc.nasa.gov/Tools/name_or_coordinates_help.html"
    )

    assert data.coordinate.frame == "galactic"
    assert data.coordinate.origin == "sun"
