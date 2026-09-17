from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)
from astrosphere.models.scientific import (
    ScientificData,
    SpaceWeatherData,
)


def extract_ai_facts(
    object_id,
    results,
):
    if not isinstance(object_id, str) or not object_id.strip():
        raise ValueError("Object ID is required.")

    if not isinstance(results, tuple):
        results = tuple(results)

    facts = []
    provenance = []
    observation_time = None

    for result in results:
        if not isinstance(
            result,
            CapabilityExecutionResult,
        ):
            raise ValueError(
                "AI facts require "
                "CapabilityExecutionResult instances."
            )

        extracted = _extract_result_facts(result)

        facts.extend(extracted["facts"])

        if (
            observation_time is None
            and extracted["observation_time"] is not None
        ):
            observation_time = (
                extracted["observation_time"]
            )

        for source in extracted["provenance"]:
            if source not in provenance:
                provenance.append(source)

    return AIFactSet(
        object_id=object_id.strip().lower(),
        facts=tuple(facts),
        observation_time=observation_time,
        provenance=tuple(provenance),
    )


def _extract_result_facts(result):
    capability_id = result.capability_id
    value = result.result

    if capability_id == "scientific-data":
        return _extract_scientific_data(
            value,
            capability_id,
        )

    if capability_id == "space-weather":
        return _extract_space_weather(
            value,
            capability_id,
        )

    if capability_id == "close-approaches":
        return _extract_close_approaches(
            value,
            capability_id,
        )

    if capability_id == "trajectory":
        return _extract_trajectory(
            value,
            capability_id,
        )

    if capability_id == "orbital-analysis":
        return _extract_orbital_analysis(
            value,
            capability_id,
        )

    return {
        "facts": (),
        "observation_time": None,
        "provenance": (),
    }


def _extract_scientific_data(
    value,
    capability_id,
):
    if not isinstance(value, ScientificData):
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    facts = []

    observation_time = None

    if value.observation is not None:
        observation_time = (
            value.observation.observation_time
        )

    provenance = ()

    if value.provenance is not None:
        provenance = value.provenance.sources

    fact_source = None

    if len(provenance) == 1:
        fact_source = provenance[0]

    if value.position is not None:
        position = value.position

        facts.extend(
            (
                AIFact(
                    name="position_x",
                    value=position.x,
                    unit=position.unit,
                    source_capability=capability_id,
                    source=fact_source,
                    metadata={
                        "frame": position.frame,
                    },
                ),
                AIFact(
                    name="position_y",
                    value=position.y,
                    unit=position.unit,
                    source_capability=capability_id,
                    source=fact_source,
                    metadata={
                        "frame": position.frame,
                    },
                ),
                AIFact(
                    name="position_z",
                    value=position.z,
                    unit=position.unit,
                    source_capability=capability_id,
                    source=fact_source,
                    metadata={
                        "frame": position.frame,
                    },
                ),
            )
        )

    if value.velocity is not None:
        velocity = value.velocity

        facts.extend(
            (
                AIFact(
                    name="velocity_x",
                    value=velocity.x,
                    unit=velocity.unit,
                    source_capability=capability_id,
                    source=fact_source,
                    metadata={
                        "frame": velocity.frame,
                    },
                ),
                AIFact(
                    name="velocity_y",
                    value=velocity.y,
                    unit=velocity.unit,
                    source_capability=capability_id,
                    source=fact_source,
                    metadata={
                        "frame": velocity.frame,
                    },
                ),
                AIFact(
                    name="velocity_z",
                    value=velocity.z,
                    unit=velocity.unit,
                    source_capability=capability_id,
                    source=fact_source,
                    metadata={
                        "frame": velocity.frame,
                    },
                ),
            )
        )

    provenance = ()

    if value.provenance is not None:
        provenance = value.provenance.sources

    return {
        "facts": tuple(facts),
        "observation_time": observation_time,
        "provenance": tuple(provenance),
    }


def _extract_space_weather(
    value,
    capability_id,
):
    if not isinstance(value, SpaceWeatherData):
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    facts = []

    if value.solar_wind is not None:
        wind = value.solar_wind

        if wind.speed_km_s is not None:
            facts.append(
                AIFact(
                    name="solar_wind_speed",
                    value=wind.speed_km_s,
                    unit="km/s",
                    source_capability=capability_id,
                )
            )

        if wind.density_cm3 is not None:
            facts.append(
                AIFact(
                    name="solar_wind_density",
                    value=wind.density_cm3,
                    unit="cm^-3",
                    source_capability=capability_id,
                )
            )

        if wind.temperature_k is not None:
            facts.append(
                AIFact(
                    name="solar_wind_temperature",
                    value=wind.temperature_k,
                    unit="K",
                    source_capability=capability_id,
                )
            )

    if value.magnetic_field is not None:
        magnetic = value.magnetic_field

        if magnetic.bt_nt is not None:
            facts.append(
                AIFact(
                    name="magnetic_field_bt",
                    value=magnetic.bt_nt,
                    unit="nT",
                    source_capability=capability_id,
                    metadata={
                        "component": "Bt",
                    },
                )
            )

        if magnetic.bz_nt is not None:
            facts.append(
                AIFact(
                    name="magnetic_field_bz_gsm",
                    value=magnetic.bz_nt,
                    unit="nT",
                    source_capability=capability_id,
                    metadata={
                        "component": "Bz",
                        "frame": "GSM",
                    },
                )
            )

    if value.geomagnetic is not None:
        if value.geomagnetic.kp is not None:
            facts.append(
                AIFact(
                    name="geomagnetic_kp",
                    value=value.geomagnetic.kp,
                    source_capability=capability_id,
                )
            )

    provenance = ()

    if value.provenance is not None:
        provenance = value.provenance.sources

    return {
        "facts": tuple(facts),
        "observation_time": value.observation_time,
        "provenance": tuple(provenance),
    }


def _extract_close_approaches(
    value,
    capability_id,
):
    if not isinstance(value, (list, tuple)):
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    facts = []
    provenance = []
    observation_time = None

    for index, approach in enumerate(value):
        if not hasattr(
            approach,
            "close_approach_time",
        ):
            continue

        facts.extend(
            (
                AIFact(
                    name="close_approach_time",
                    value=approach.close_approach_time,
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                ),
                AIFact(
                    name="close_approach_distance",
                    value=approach.distance_au,
                    unit="AU",
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                ),
                AIFact(
                    name="close_approach_distance_km",
                    value=approach.distance_km,
                    unit="km",
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                ),
                AIFact(
                    name="close_approach_relative_velocity",
                    value=approach.relative_velocity_km_s,
                    unit="km/s",
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                ),
            )
        )

        if approach.source is not None:
            if approach.source not in provenance:
                provenance.append(
                    approach.source
                )

    return {
        "facts": tuple(facts),
        "observation_time": observation_time,
        "provenance": tuple(provenance),
    }


def _extract_trajectory(
    value,
    capability_id,
):
    if not isinstance(value, dict):
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    facts = []

    if value.get("observation_time") is not None:
        facts.append(
            AIFact(
                name="trajectory_observation_time",
                value=value["observation_time"],
                source_capability=capability_id,
            )
        )

    if value.get("orbital_period_days") is not None:
        facts.append(
            AIFact(
                name="orbital_period",
                value=value["orbital_period_days"],
                unit="days",
                source_capability=capability_id,
            )
        )

    if value.get("samples") is not None:
        facts.append(
            AIFact(
                name="trajectory_sample_count",
                value=value["samples"],
                source_capability=capability_id,
            )
        )

    if value.get("coordinate_frame") is not None:
        facts.append(
            AIFact(
                name="trajectory_coordinate_frame",
                value=value["coordinate_frame"],
                source_capability=capability_id,
            )
        )

    return {
        "facts": tuple(facts),
        "observation_time": value.get(
            "observation_time"
        ),
        "provenance": (),
    }


def _extract_orbital_analysis(
    value,
    capability_id,
):
    if not isinstance(value, (list, tuple)):
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    facts = []

    for index, measurement in enumerate(value):
        if not isinstance(
            measurement,
            dict,
        ):
            continue

        if measurement.get("date") is not None:
            facts.append(
                AIFact(
                    name="analysis_date",
                    value=measurement["date"],
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                )
            )

        if measurement.get("distance_km") is not None:
            facts.append(
                AIFact(
                    name="body_distance",
                    value=measurement["distance_km"],
                    unit="km",
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                )
            )

        if measurement.get(
            "relative_velocity_km_s"
        ) is not None:
            facts.append(
                AIFact(
                    name="relative_velocity",
                    value=measurement[
                        "relative_velocity_km_s"
                    ],
                    unit="km/s",
                    source_capability=capability_id,
                    metadata={
                        "index": index,
                    },
                )
            )

    return {
        "facts": tuple(facts),
        "observation_time": None,
        "provenance": (),
    }
