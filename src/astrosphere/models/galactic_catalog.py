from dataclasses import dataclass

from astrosphere.models.galactic import GalacticCoordinate
from astrosphere.models.scientific import DataSource


@dataclass(frozen=True)
class GalacticCoordinateData:
    object_id: str
    source: DataSource
    coordinate: GalacticCoordinate


_HEASARC_GALACTIC_SOURCE = DataSource(
    name="HEASARC Galactic Coordinate System",
    provider="NASA Goddard Space Flight Center HEASARC",
    url="https://heasarc.gsfc.nasa.gov/Tools/name_or_coordinates_help.html",
    dataset="Galactic Coordinates",
)


GALACTIC_COORDINATE_DATA = {
    "sun": GalacticCoordinateData(
        object_id="sun",
        source=_HEASARC_GALACTIC_SOURCE,
        coordinate=GalacticCoordinate(
            longitude_deg=0.0,
            latitude_deg=0.0,
            distance_pc=0.0,
            frame="galactic",
            origin="sun",
            source=_HEASARC_GALACTIC_SOURCE,
        ),
    ),
}


def get_galactic_coordinate_data(
    object_id,
):
    if not isinstance(object_id, str):
        return None

    return GALACTIC_COORDINATE_DATA.get(
        object_id.strip().lower()
    )
