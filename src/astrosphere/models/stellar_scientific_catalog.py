from astrosphere.models.scientific import DataSource
from astrosphere.models.stellar_scientific import (
    StellarScientificProperties,
)


_SUN_SOURCE = DataSource(
    name="NASA Sun Fact Sheet",
    provider="NASA Goddard Space Flight Center NSSDCA",
    url="https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html",
    dataset="Sun Fact Sheet",
)

_SIRIUS_SOURCE = DataSource(
    name="NASA Hubble Sirius Observation",
    provider="NASA Hubble Space Telescope",
    url="https://science.nasa.gov/asset/hubble/the-dog-star-sirius-and-its-tiny-companion/",
    dataset="Sirius A and Sirius B",
)

_PROXIMA_SOURCE = DataSource(
    name="NASA Hubble Proxima Centauri",
    provider="NASA Hubble Space Telescope",
    url="https://science.nasa.gov/asset/hubble/proxima-centauri/",
    dataset="Proxima Centauri",
)

_BETELGEUSE_SOURCE = DataSource(
    name="NASA Betelgeuse Science",
    provider="NASA Science",
    url="https://science.nasa.gov/universe/what-is-betelgeuse-inside-the-strange-volatile-star/",
    dataset="Betelgeuse",
)

_VEGA_SOURCE = DataSource(
    name="NASA Stellar Characteristics",
    provider="NASA Technical Reports Server",
    url="https://ntrs.nasa.gov/api/citations/19940022286/downloads/19940022286.pdf",
    dataset="Stellar Characteristics",
)


STELLAR_SCIENTIFIC_PROPERTIES = {
    "sun": StellarScientificProperties(
        object_id="sun",
        source=_SUN_SOURCE,
        physical_properties={
            "mass_kg": 1.9884e30,
            "mean_radius_km": 695700.0,
            "luminosity_w": 3.828e26,
            "effective_temperature_k": 5772.0,
        },
        stellar_properties={
            "spectral_type": "G2 V",
        },
    ),
    "sirius": StellarScientificProperties(
        object_id="sirius",
        source=_SIRIUS_SOURCE,
        physical_properties={
            "mass_solar": 2.0,
            "diameter_km": 2.4e6,
            "effective_temperature_k": 10500.0,
            "distance_pc": 2.6,
        },
        stellar_properties={
            "system_type": "binary",
            "primary_component": "Sirius A",
            "companion_component": "Sirius B",
        },
    ),
    "proxima-centauri": StellarScientificProperties(
        object_id="proxima-centauri",
        source=_PROXIMA_SOURCE,
        physical_properties={
            "mass_solar": 0.125,
            "distance_light_years": 4.24,
        },
        stellar_properties={
            "spectral_type": "M5.5Ve",
            "stellar_class": "main sequence",
            "variable_type": "flare star",
        },
    ),
    "betelgeuse": StellarScientificProperties(
        object_id="betelgeuse",
        source=_BETELGEUSE_SOURCE,
        physical_properties={
            "mass_solar": 15.0,
            "radius_solar": 700.0,
            "distance_light_years": 700.0,
            "effective_temperature_k": 3573.0,
        },
        stellar_properties={
            "stellar_class": "red supergiant",
            "variable": True,
        },
    ),
    "vega": StellarScientificProperties(
        object_id="vega",
        source=_VEGA_SOURCE,
        physical_properties={
            "mass_solar": 2.5,
            "luminosity_solar": 60.0,
            "distance_pc": 8.1,
        },
        stellar_properties={
            "spectral_type": "A0Va",
        },
    ),
}


def get_stellar_scientific_properties(
    object_id,
):
    if not isinstance(object_id, str):
        return None

    return STELLAR_SCIENTIFIC_PROPERTIES.get(
        object_id.strip().lower()
    )
