from astrosphere.ai.context import AIObjectGraph
from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)
from astrosphere.models.scientific import (
    ScientificData,
    SpaceWeatherData,
)


def extract_ai_facts(
    object_id,
    results,
    object_graph=None,
    question=None,
):
    if not isinstance(object_id, str) or not object_id.strip():
        raise ValueError("Object ID is required.")

    if not isinstance(results, tuple):
        results = tuple(results)

    facts = []
    provenance = []
    observation_time = None

    if object_graph is not None and not isinstance(
        object_graph,
        AIObjectGraph,
    ):
        raise ValueError(
            "object_graph must be an AIObjectGraph instance."
        )

    if object_graph is not None:
        facts.extend(
            _extract_object_graph_facts(
                object_graph,
                question=question,
            )
        )

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


def _extract_object_graph_facts(
    object_graph,
    question=None,
):
    facts = []

    normalized_question = (
        question.strip().lower()
        if isinstance(question, str)
        else ""
    )

    if object_graph.parent is not None:
        facts.append(
            AIFact(
                name="object_parent",
                value=object_graph.parent.id,
                source_capability="relationships",
                metadata={
                    "name": object_graph.parent.name,
                    "object_type": object_graph.parent.object_type,
                },
            )
        )

    for ancestor in object_graph.ancestors:
        facts.append(
            AIFact(
                name="object_ancestor",
                value=ancestor.id,
                source_capability="relationships",
                metadata={
                    "name": ancestor.name,
                    "object_type": ancestor.object_type,
                },
            )
        )

    for child in object_graph.children:
        facts.append(
            AIFact(
                name="object_child",
                value=child.id,
                source_capability="relationships",
                metadata={
                    "name": child.name,
                    "object_type": child.object_type,
                },
            )
        )


    for relationship in object_graph.relationships:
        target_object = get_celestial_object(
            relationship.target_id
        )

        metadata = {}

        if target_object is not None:
            metadata = {
                "name": target_object.name,
                "object_type": target_object.object_type,
            }

        fact_name = (
            f"relationship_{relationship.relationship_type}"
        )

        facts.append(
            AIFact(
                name=fact_name,
                value=relationship.target_id,
                source_capability="relationships",
                metadata=metadata,
            )
        )
    if "what orbits" in normalized_question:
        for relationship in object_graph.incoming_relationships:
            if relationship.relationship_type != "orbits":
                continue
            source_object = get_celestial_object(
                relationship.source_id
            )

            metadata = {}

            if source_object is not None:
                metadata = {
                    "name": source_object.name,
                    "object_type": source_object.object_type,
                }

            fact_name = (
                f"incoming_relationship_"
                f"{relationship.relationship_type}"
            )

            facts.append(
                AIFact(
                    name=fact_name,
                    value=relationship.source_id,
                    source_capability="relationships",
                    metadata=metadata,
                )
            )

    if "associated" in normalized_question:
        associated_ids = []

        if object_graph.parent is not None:
            associated_ids.append(object_graph.parent.id)

        for child in object_graph.children:
            associated_ids.append(child.id)

        for relationship in object_graph.relationships:
            associated_ids.append(relationship.target_id)

        for relationship in object_graph.incoming_relationships:
            associated_ids.append(relationship.source_id)

        seen_ids = set()

        for associated_id in associated_ids:
            if associated_id in seen_ids:
                continue

            seen_ids.add(associated_id)

            associated_object = get_celestial_object(
                associated_id
            )

            metadata = {}

            if associated_object is not None:
                metadata = {
                    "name": associated_object.name,
                    "object_type": associated_object.object_type,
                }

            facts.append(
                AIFact(
                    name="associated_object",
                    value=associated_id,
                    source_capability="relationships",
                    metadata=metadata,
                )
            )
    return tuple(facts)

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

    if capability_id == "planetary-trajectory":
        return _extract_planetary_trajectory(
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

    if value.physical_properties:
        for name, property_value in value.physical_properties.items():
            fact_name = f"physical_{name}"

            facts.append(
                AIFact(
                    name=fact_name,
                    value=property_value,
                    source_capability=capability_id,
                    source=(
                        value.physical_properties_source
                        if value.physical_properties_source is not None
                        else fact_source
                    ),
                )
            )

    if value.stellar_properties:
        for name, property_value in value.stellar_properties.items():
            fact_name = f"stellar_{name}"

            facts.append(
                AIFact(
                    name=fact_name,
                    value=property_value,
                    source_capability=capability_id,
                    source=(
                        value.stellar_properties_source
                        if value.stellar_properties_source is not None
                        else fact_source
                    ),
                )
            )

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


def _extract_planetary_trajectory(
    value,
    capability_id,
):
    if not isinstance(value, (list, tuple)):
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    samples = [
        sample
        for sample in value
        if isinstance(sample, dict)
    ]

    if not samples:
        return {
            "facts": (),
            "observation_time": None,
            "provenance": (),
        }

    facts = []

    facts.append(
        AIFact(
            name="trajectory_sample_count",
            value=len(samples),
            source_capability=capability_id,
        )
    )

    first_sample = samples[0]
    last_sample = samples[-1]

    first_date = first_sample.get("date")
    last_date = last_sample.get("date")

    if first_date is not None:
        facts.append(
            AIFact(
                name="trajectory_start_date",
                value=first_date,
                source_capability=capability_id,
            )
        )

    if last_date is not None:
        facts.append(
            AIFact(
                name="trajectory_end_date",
                value=last_date,
                source_capability=capability_id,
            )
        )

    facts.append(
        AIFact(
            name="trajectory_coordinate_frame",
            value="heliocentric ecliptic",
            source_capability=capability_id,
        )
    )

    coordinate_definitions = (
        ("x_au", "trajectory_start_x", "trajectory_end_x"),
        ("y_au", "trajectory_start_y", "trajectory_end_y"),
        ("z_au", "trajectory_start_z", "trajectory_end_z"),
    )

    for coordinate_key, start_name, end_name in coordinate_definitions:
        start_value = first_sample.get(coordinate_key)
        end_value = last_sample.get(coordinate_key)

        if start_value is not None:
            facts.append(
                AIFact(
                    name=start_name,
                    value=start_value,
                    unit="AU",
                    source_capability=capability_id,
                )
            )

        if end_value is not None:
            facts.append(
                AIFact(
                    name=end_name,
                    value=end_value,
                    unit="AU",
                    source_capability=capability_id,
                )
            )

    return {
        "facts": tuple(facts),
        "observation_time": first_date,
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
