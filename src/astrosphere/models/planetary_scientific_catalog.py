from astrosphere.models.planetary_scientific import (
    PlanetaryScientificProperties,
)
from astrosphere.models.scientific import DataSource


_JPL_SOURCE = DataSource(
    name="JPL Planetary Physical Parameters",
    provider="NASA/JPL Solar System Dynamics",
    url="https://ssd.jpl.nasa.gov/planets/phys_par.html",
    dataset="Planetary Physical Parameters",
)


PLANETARY_SCIENTIFIC_PROPERTIES = {
    "mercury": PlanetaryScientificProperties(
        object_id="mercury",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 2440.53,
            "mean_radius_km": 2439.4,
            "mass_kg": 0.330103e24,
            "bulk_density_g_cm3": 5.4289,
            "equatorial_gravity_m_s2": 3.70,
            "escape_velocity_km_s": 4.25,
            "geometric_albedo": 0.106,
        },
        orbital_properties={
            "sidereal_rotation_period_days": 58.6462,
            "sidereal_orbital_period_years": 0.2408467,
        },
    ),
    "venus": PlanetaryScientificProperties(
        object_id="venus",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 6051.8,
            "mean_radius_km": 6051.8,
            "mass_kg": 4.86731e24,
            "bulk_density_g_cm3": 5.243,
            "equatorial_gravity_m_s2": 8.87,
            "escape_velocity_km_s": 10.36,
            "geometric_albedo": 0.65,
        },
        orbital_properties={
            "sidereal_rotation_period_days": -243.018,
            "sidereal_orbital_period_years": 0.61519726,
        },
    ),
    "earth": PlanetaryScientificProperties(
        object_id="earth",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 6378.1366,
            "mean_radius_km": 6371.0084,
            "mass_kg": 5.97217e24,
            "bulk_density_g_cm3": 5.5134,
            "equatorial_gravity_m_s2": 9.80,
            "escape_velocity_km_s": 11.19,
            "geometric_albedo": 0.367,
        },
        orbital_properties={
            "sidereal_rotation_period_days": 0.99726968,
            "sidereal_orbital_period_years": 1.0000174,
        },
    ),
    "mars": PlanetaryScientificProperties(
        object_id="mars",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 3396.19,
            "mean_radius_km": 3389.50,
            "mass_kg": 0.641691e24,
            "bulk_density_g_cm3": 3.9340,
            "equatorial_gravity_m_s2": 3.71,
            "escape_velocity_km_s": 5.03,
            "geometric_albedo": 0.150,
        },
        orbital_properties={
            "sidereal_rotation_period_days": 1.02595676,
            "sidereal_orbital_period_years": 1.8808476,
        },
    ),
    "jupiter": PlanetaryScientificProperties(
        object_id="jupiter",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 71492.0,
            "mean_radius_km": 69911.0,
            "mass_kg": 1898.125e24,
            "bulk_density_g_cm3": 1.3262,
            "equatorial_gravity_m_s2": 24.79,
            "escape_velocity_km_s": 60.20,
            "geometric_albedo": 0.52,
        },
        orbital_properties={
            "sidereal_rotation_period_days": 0.41354,
            "sidereal_orbital_period_years": 11.862615,
        },
    ),
    "saturn": PlanetaryScientificProperties(
        object_id="saturn",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 60268.0,
            "mean_radius_km": 58232.0,
            "mass_kg": 568.317e24,
            "bulk_density_g_cm3": 0.6871,
            "equatorial_gravity_m_s2": 10.44,
            "escape_velocity_km_s": 36.09,
            "geometric_albedo": 0.47,
        },
        orbital_properties={
            "sidereal_rotation_period_days": 0.44401,
            "sidereal_orbital_period_years": 29.447498,
        },
    ),
    "uranus": PlanetaryScientificProperties(
        object_id="uranus",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 25559.0,
            "mean_radius_km": 25362.0,
            "mass_kg": 86.8099e24,
            "bulk_density_g_cm3": 1.270,
            "equatorial_gravity_m_s2": 8.87,
            "escape_velocity_km_s": 21.38,
            "geometric_albedo": 0.51,
        },
        orbital_properties={
            "sidereal_rotation_period_days": -0.71833,
            "sidereal_orbital_period_years": 84.016846,
        },
    ),
    "neptune": PlanetaryScientificProperties(
        object_id="neptune",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 24764.0,
            "mean_radius_km": 24622.0,
            "mass_kg": 102.4092e24,
            "bulk_density_g_cm3": 1.638,
            "equatorial_gravity_m_s2": 11.15,
            "escape_velocity_km_s": 23.56,
            "geometric_albedo": 0.41,
        },
        orbital_properties={
            "sidereal_rotation_period_days": 0.67125,
            "sidereal_orbital_period_years": 164.79132,
        },
    ),
    "pluto": PlanetaryScientificProperties(
        object_id="pluto",
        source=_JPL_SOURCE,
        physical_properties={
            "equatorial_radius_km": 1188.3,
            "mean_radius_km": 1188.3,
            "mass_kg": 13024.6e18,
            "bulk_density_g_cm3": 1.853,
            "equatorial_gravity_m_s2": 0.62,
            "escape_velocity_km_s": 1.21,
            "geometric_albedo": 0.3,
        },
        orbital_properties={
            "sidereal_rotation_period_days": -6.3872,
            "sidereal_orbital_period_years": 247.92065,
        },
    ),
}


def get_planetary_scientific_properties(
    object_id,
):
    return PLANETARY_SCIENTIFIC_PROPERTIES.get(
        object_id.strip().lower()
    )
