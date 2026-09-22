from astrosphere.ai.explanation import (
    AIExplanation,
    AIExplanationSet,
)
from astrosphere.ai.facts import AIFactSet
from astrosphere.ai.interpretation import AIInterpretationSet


_CONCEPT_DESCRIPTIONS = {
    "position": (
        "The position facts describe where the object is located "
        "in the supplied reference frame."
    ),
    "velocity": (
        "The velocity facts describe how the object's position "
        "is changing over time."
    ),
    "trajectory": (
        "The trajectory information describes the object's path "
        "through space over the supplied time range."
    ),
    "close_approach": (
        "The close-approach information describes when the object "
        "reaches a minimum separation from another object."
    ),
    "space_weather": (
        "The space-weather facts describe measured or derived "
        "conditions in near-Earth space."
    ),
    "solar_wind": (
        "The solar-wind facts describe properties of the charged "
        "particle flow from the Sun."
    ),
    "magnetic_field": (
        "The magnetic-field facts describe the measured magnetic "
        "environment represented by the supplied data."
    ),
    "geomagnetic": (
        "The geomagnetic facts describe the state of Earth's "
        "magnetic environment."
    ),
}


def _matching_fact_names(
    fact_set,
    subject,
):
    prefixes = {
        "position": ("position_",),
        "velocity": ("velocity_",),
        "trajectory": (
            "trajectory_",
            "orbital_period",
            "trajectory_samples",
        ),
        "close_approach": (
            "approach_",
            "close_approach_",
        ),
        "space_weather": (
            "solar_wind_",
            "bt_",
            "bz_",
            "kp",
        ),
        "solar_wind": (
            "solar_wind_",
        ),
        "magnetic_field": (
            "bt_",
            "bz_",
        ),
        "geomagnetic": (
            "kp",
        ),
    }

    subject_prefixes = prefixes.get(subject, ())

    return tuple(
        fact.name
        for fact in fact_set.facts
        if fact.name.startswith(subject_prefixes)
        or (
            subject == "space_weather"
            and fact.name in {
                "solar_wind_speed",
                "solar_wind_density",
                "solar_wind_temperature",
                "magnetic_field_bt",
                "magnetic_field_bz_gsm",
                "geomagnetic_kp",
            }
        )
    )


def _matching_interpretations(
    interpretation_set,
    fact_names,
):
    return tuple(
        interpretation.statement
        for interpretation in interpretation_set.interpretations
        if any(
            fact_name in interpretation.supporting_facts
            for fact_name in fact_names
        )
    )


def build_fact_grounded_explanation(
    object_id,
    fact_set,
    interpretation_set,
    subject,
    level="standard",
):
    if not isinstance(object_id, str) or not object_id.strip():
        raise ValueError("Object ID is required.")

    if not isinstance(fact_set, AIFactSet):
        raise ValueError("AIFactSet is required.")

    if not isinstance(
        interpretation_set,
        AIInterpretationSet,
    ):
        raise ValueError(
            "AIInterpretationSet is required."
        )

    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("Explanation subject is required.")

    if not isinstance(level, str) or not level.strip():
        raise ValueError("Explanation level is required.")

    normalized_subject = subject.strip().lower()
    normalized_level = level.strip().lower()

    if normalized_subject not in _CONCEPT_DESCRIPTIONS:
        raise ValueError(
            f"Unsupported grounded concept: {normalized_subject}"
        )

    if normalized_level not in {
        "beginner",
        "standard",
        "detailed",
    }:
        raise ValueError(
            f"Unsupported explanation level: {normalized_level}"
        )

    fact_names = _matching_fact_names(
        fact_set,
        normalized_subject,
    )

    if not fact_names:
        raise ValueError(
            f"No supporting facts available for: "
            f"{normalized_subject}"
        )

    interpretation_statements = _matching_interpretations(
        interpretation_set,
        fact_names,
    )

    provenance = tuple(fact_set.provenance)

    for source in interpretation_set.provenance:
        if source not in provenance:
            provenance += (source,)

    uncertainties = tuple(fact_set.uncertainties)

    for uncertainty in interpretation_set.uncertainties:
        if uncertainty not in uncertainties:
            uncertainties += (uncertainty,)

    explanation = AIExplanation(
        subject=normalized_subject,
        explanation=_CONCEPT_DESCRIPTIONS[
            normalized_subject
        ],
        level=normalized_level,
        supporting_facts=fact_names,
        supporting_interpretations=(
            interpretation_statements
        ),
        observation_time=(
            fact_set.observation_time
            or interpretation_set.observation_time
        ),
        provenance=provenance,
        uncertainties=uncertainties,
    )

    return AIExplanationSet(
        object_id=object_id.strip().lower(),
        explanations=(explanation,),
        level=normalized_level,
        observation_time=explanation.observation_time,
        provenance=provenance,
        uncertainties=uncertainties,
    )
