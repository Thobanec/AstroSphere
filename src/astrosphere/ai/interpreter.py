from astrosphere.ai.facts import (
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretation,
    AIInterpretationSet,
)


def interpret_ai_facts(
    subject,
    fact_set,
):
    if not isinstance(fact_set, AIFactSet):
        raise ValueError(
            "AIFactSet is required."
        )

    if not isinstance(subject, str):
        raise ValueError(
            "Interpretation subject is required."
        )

    subject = subject.strip()

    if not subject:
        raise ValueError(
            "Interpretation subject is required."
        )

    interpretations = tuple(
        _interpret_fact(
            subject,
            fact,
        )
        for fact in fact_set.facts
    )

    return AIInterpretationSet(
        object_id=fact_set.object_id,
        interpretations=interpretations,
        observation_time=fact_set.observation_time,
        provenance=fact_set.provenance,
        uncertainties=fact_set.uncertainties,
    )


def _interpret_fact(
    subject,
    fact,
):
    value_text = str(fact.value)

    if fact.unit:
        statement = (
            f"{subject} {fact.name} is "
            f"{value_text} {fact.unit}."
        )
    else:
        statement = (
            f"{subject} {fact.name} is "
            f"{value_text}."
        )

    supporting_capabilities = ()

    if fact.source_capability:
        supporting_capabilities = (
            fact.source_capability,
        )

    provenance = ()

    if fact.source is not None:
        provenance = (
            fact.source,
        )

    return AIInterpretation(
        subject=subject,
        statement=statement,
        supporting_facts=(fact.name,),
        supporting_capabilities=supporting_capabilities,
        observation_time=None,
        provenance=provenance,
        uncertainties=(),
    )
