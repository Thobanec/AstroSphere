from astrosphere.models.galactic import GalacticCoordinate
from astrosphere.models.scientific_serialization import (
    _data_source_to_dict,
)


def galactic_coordinate_to_dict(
    coordinate: GalacticCoordinate,
):
    return {
        "longitude_deg": coordinate.longitude_deg,
        "latitude_deg": coordinate.latitude_deg,
        "distance_pc": coordinate.distance_pc,
        "frame": coordinate.frame,
        "origin": coordinate.origin,
        "source": _data_source_to_dict(
            coordinate.source
        ),
    }
