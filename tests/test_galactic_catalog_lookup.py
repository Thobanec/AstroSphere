from astrosphere.models.galactic import (
    GalacticCoordinate,
)
from astrosphere.models.galactic_catalog import (
    get_galactic_coordinate_data,
)


def test_galactic_coordinate_registry_returns_coordinate():
    data = get_galactic_coordinate_data("sun")

    assert data is not None
    assert isinstance(
        data.coordinate,
        GalacticCoordinate,
    )


def test_galactic_coordinate_registry_is_case_insensitive():
    data = get_galactic_coordinate_data("SUN")

    assert data is not None
    assert isinstance(
        data.coordinate,
        GalacticCoordinate,
    )


def test_galactic_coordinate_registry_returns_none_for_unknown_object():
    data = get_galactic_coordinate_data(
        "unknown-object"
    )

    assert data is None
