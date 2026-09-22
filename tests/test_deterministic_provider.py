from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.ai.fact_extractor import (
    AIFact,
    AIFactSet,
)

def test_render_associated_objects():
    provider = DeterministicLanguageProvider()

    facts = AIFactSet(object_id="earth",
        facts=(
            AIFact(
                name="associated_object",
                value="sun",
                source_capability="relationships",
                metadata={
                    "name": "Sun",
                    "object_type": "star",
                },
            ),
            AIFact(
                name="associated_object",
                value="moon",
                source_capability="relationships",
                metadata={
                    "name": "Moon",
                    "object_type": "moon",
                },
            ),
            AIFact(
                name="associated_object",
                value="spacecraft:25544",
                source_capability="relationships",
                metadata={
                    "name": "ISS",
                    "object_type": "spacecraft",
                },
            ),
        )
    )

    answer = provider._render_associated_objects(
        "Earth",
        facts.facts,
    )

    assert answer == (
        "Earth is associated with Sun, Moon, and ISS."
    )
