from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.ai.explanation import (
    AIExplanation,
    AIExplanationSet,
)
from astrosphere.ai.facts import (
    AIFact,
    AIFactSet,
)
from astrosphere.ai.interpretation import (
    AIInterpretationSet,
)
from astrosphere.ai.llm import (
    AILanguageRequest,
)
from astrosphere.models.celestial import (
    CelestialObject,
)
from astrosphere.models.scientific import (
    DataSource,
)
def test_deterministic_provider_renders_grounded_facts():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="What is the position of Earth?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="position_x",
                    value=1.5,
                    unit="AU",
                    source_capability="scientific-data",
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "Grounded scientific information for Earth:\n"
        "position_x: 1.5 AU"
    )


def test_deterministic_provider_renders_planetary_trajectory():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="Show the trajectory of Earth.",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="trajectory_sample_count",
                    value=5,
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_start_date",
                    value="2026-09-19T00:00:00+00:00",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_end_date",
                    value="2026-10-19T00:00:00+00:00",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_coordinate_frame",
                    value="heliocentric ecliptic",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_start_x",
                    value=1.0,
                    unit="AU",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_start_y",
                    value=0.0,
                    unit="AU",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_start_z",
                    value=0.0,
                    unit="AU",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_end_x",
                    value=0.9,
                    unit="AU",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_end_y",
                    value=0.4,
                    unit="AU",
                    source_capability="planetary-trajectory",
                ),
                AIFact(
                    name="trajectory_end_z",
                    value=0.0,
                    unit="AU",
                    source_capability="planetary-trajectory",
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "Earth trajectory:\n"
        "Calculated from 2026-09-19T00:00:00+00:00 "
        "to 2026-10-19T00:00:00+00:00.\n"
        "Trajectory samples: 5.\n"
        "Reference frame: heliocentric ecliptic.\n"
        "Start position: (1.000, 0.000, 0.000) AU.\n"
        "End position: (0.900, 0.400, 0.000) AU."
    )

def test_deterministic_provider_renders_explanations():
    provider = DeterministicLanguageProvider()

    explanation = AIExplanation(
        subject="velocity",
        explanation=(
            "Velocity describes how an object's position "
            "changes over time."
        ),
        level="standard",
        explanation_type="what",
        supporting_facts=("velocity_x",),
        supporting_interpretations=(
            "Velocity fact velocity_x is 5.0 km/s.",
        ),
    )

    request = AILanguageRequest(
        question="What is velocity?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="velocity_x",
                    value=5.0,
                    unit="km/s",
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
        explanations=AIExplanationSet(
            object_id="earth",
            explanations=(explanation,),
            level="standard",
        ),
    )

    response = provider.generate(request)

    assert (
        "Grounded scientific information for Earth:"
        in response.answer
    )
    assert "velocity_x: 5.0 km/s" in response.answer
    assert "Scientific explanation:" in response.answer
    assert (
        "velocity (what, standard): "
        "Velocity describes how an object's position "
        "changes over time."
        in response.answer
    )


def test_deterministic_provider_preserves_provenance():
    provider = DeterministicLanguageProvider()

    source = DataSource(
        name="Test Source",
        provider="Test Provider",
        dataset="Test Dataset",
    )

    request = AILanguageRequest(
        question="Describe Earth.",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
        provenance=(source,),
        uncertainties=("Example uncertainty",),
    )

    response = provider.generate(request)

    assert response.provenance == (source,)
    assert response.uncertainties == (
        "Example uncertainty",
    )


def test_deterministic_provider_handles_empty_facts():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="Describe Earth.",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "No grounded scientific facts are "
        "available for Earth."
    )


def test_deterministic_provider_rejects_invalid_request():
    provider = DeterministicLanguageProvider()

    try:
        provider.generate(None)
    except ValueError as exc:
        assert str(exc) == (
            "AILanguageRequest is required."
        )
    else:
        raise AssertionError(
            "Invalid language requests must be rejected."
        )



def test_deterministic_provider_answers_what_does_object_orbit():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="What does Earth orbit?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="relationship_orbits",
                    value="sun",
                    source_capability="relationships",
                    metadata={
                        "name": "Sun",
                        "object_type": "star",
                    },
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "Earth orbits the Sun."
    )


def test_deterministic_provider_answers_what_orbits_object():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="What orbits Earth?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="incoming_relationship_orbits",
                    value="moon",
                    source_capability="relationships",
                    metadata={
                        "name": "Moon",
                        "object_type": "moon",
                    },
                ),
                AIFact(
                    name="incoming_relationship_orbits",
                    value="spacecraft:25544",
                    source_capability="relationships",
                    metadata={
                        "name": "ISS",
                        "object_type": "spacecraft",
                    },
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "The Moon and ISS orbit Earth."
    )


def test_deterministic_provider_answers_cosmic_hierarchy():
    provider = DeterministicLanguageProvider()

    request = AILanguageRequest(
        question="Where is Earth in the cosmic hierarchy?",
        object=CelestialObject(
            id="earth",
            name="Earth",
            object_type="planet",
        ),
        facts=AIFactSet(
            object_id="earth",
            facts=(
                AIFact(
                    name="object_parent",
                    value="sun",
                    source_capability="relationships",
                    metadata={
                        "name": "Sun",
                        "object_type": "star",
                    },
                ),
                AIFact(
                    name="object_ancestor",
                    value="sun",
                    source_capability="relationships",
                    metadata={
                        "name": "Sun",
                        "object_type": "star",
                    },
                ),
                AIFact(
                    name="object_ancestor",
                    value="solar-system",
                    source_capability="relationships",
                    metadata={
                        "name": "Solar System",
                        "object_type": "system",
                    },
                ),
                AIFact(
                    name="object_ancestor",
                    value="milky-way",
                    source_capability="relationships",
                    metadata={
                        "name": "Milky Way",
                        "object_type": "galaxy",
                    },
                ),
                AIFact(
                    name="object_ancestor",
                    value="universe",
                    source_capability="relationships",
                    metadata={
                        "name": "Universe",
                        "object_type": "universe",
                    },
                ),
            ),
        ),
        interpretations=AIInterpretationSet(
            object_id="earth",
        ),
    )

    response = provider.generate(request)

    assert response.answer == (
        "Earth is in the following cosmic hierarchy: "
        "Earth → Sun → Solar System → Milky Way → Universe."
    )
