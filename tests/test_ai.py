from astrosphere.ai import AIContext
from astrosphere.capabilities.definitions import CapabilityDefinition
from astrosphere.capabilities.results import CapabilityExecutionResult
from astrosphere.models.celestial import CelestialObject
from astrosphere.models.scientific import DataSource


def test_ai_context_can_reference_canonical_object():
    earth = CelestialObject(
        id="earth",
        name="Earth",
        object_type="planet",
        parent_id="sun",
        system_id="solar-system",
    )

    context = AIContext(
        question="What is Earth?",
        object=earth,
    )

    assert context.question == "What is Earth?"
    assert context.object is earth
    assert context.object.id == "earth"
    assert context.object.object_type == "planet"


def test_ai_context_defaults_are_empty():
    context = AIContext(
        question="What is the Solar System?",
    )

    assert context.object is None
    assert context.scientific_data is None
    assert context.capabilities == ()
    assert context.capability_results == ()
    assert context.provenance == ()
    assert context.uncertainties == ()
    assert context.metadata is None


def test_ai_context_can_hold_capabilities_and_results():
    capability = CapabilityDefinition(
        id="context",
        name="Object Context",
        description="Provide celestial object context.",
    )

    result = CapabilityExecutionResult(
        object_id="earth",
        capability_id="context",
        result={"object_id": "earth"},
    )

    context = AIContext(
        question="Tell me about Earth.",
        capabilities=(capability,),
        capability_results=(result,),
    )

    assert context.capabilities == (capability,)
    assert context.capability_results == (result,)


def test_ai_context_can_hold_provenance_and_uncertainty():
    source = DataSource(
        name="JPL DE440S",
        provider="NASA/JPL",
        dataset="DE440S",
    )

    context = AIContext(
        question="Where is Earth?",
        provenance=(source,),
        uncertainties=("Observation time was not explicitly provided.",),
    )

    assert context.provenance == (source,)
    assert context.provenance[0].name == "JPL DE440S"
    assert context.uncertainties == (
        "Observation time was not explicitly provided.",
    )


def test_ai_context_is_immutable():
    context = AIContext(
        question="What is Earth?",
    )

    try:
        context.question = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("AIContext should be immutable.")
