import pytest

from astrosphere.ai import build_ai_context


def test_build_ai_context_for_earth():
    context = build_ai_context(
        "Where is Earth?",
        "earth",
    )

    assert context.question == "Where is Earth?"
    assert context.object.id == "earth"
    assert context.object.name == "Earth"
    assert context.scientific_data is not None

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert "context" in capability_ids
    assert "scientific-data" in capability_ids
    assert "relationships" in capability_ids
    assert "space-weather" in capability_ids
    assert "orbital-analysis" in capability_ids

    provenance_names = {
        source.name
        for source in context.provenance
    }

    assert "JPL DE440S" in provenance_names


def test_build_ai_context_for_apophis():
    context = build_ai_context(
        "Where is Apophis?",
        "asteroid:99942",
    )

    assert context.object.id == "asteroid:99942"
    assert context.object.name == "Apophis"
    assert context.scientific_data is not None

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert "tracking" in capability_ids
    assert "trajectory" in capability_ids
    assert "close-approaches" in capability_ids

    provenance_names = {
        source.name
        for source in context.provenance
    }

    assert "Minor Planet Center" in provenance_names


def test_build_ai_context_for_iss():
    context = build_ai_context(
        "Where is the ISS?",
        "spacecraft:25544",
    )

    assert context.object.id == "spacecraft:25544"
    assert context.object.name == "ISS"
    assert context.scientific_data is not None

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert "tracking" in capability_ids

    provenance_names = {
        source.name
        for source in context.provenance
    }

    assert provenance_names


def test_build_ai_context_for_sun_uses_grounded_scientific_data():

    context = build_ai_context(
        "What is the Sun?",
        "sun",
    )

    assert context.object.id == "sun"
    assert context.object.name == "Sun"

    assert context.scientific_data is not None

    assert (
        context.scientific_data.object_id
        == "sun"
    )

    assert (
        context.scientific_data.physical_properties
    )

    provenance_names = {
        source.name
        for source in context.provenance
    }

    assert "NASA Sun Fact Sheet" in provenance_names

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert capability_ids == {
        "context",
        "scientific-data",
        "relationships",
    }

def test_build_ai_context_rejects_unknown_object():
    with pytest.raises(
        ValueError,
        match="Unknown celestial object",
    ):
        build_ai_context(
            "Tell me about Vulcan.",
            "unknown-object",
        )


def test_build_ai_context_rejects_empty_question():
    with pytest.raises(
        ValueError,
        match="AI question is required",
    ):
        build_ai_context(
            "",
            "earth",
        )


def test_build_ai_context_rejects_empty_object_id():
    with pytest.raises(
        ValueError,
        match="Celestial object ID is required",
    ):
        build_ai_context(
            "Where is Earth?",
            "",
        )


def test_build_ai_context_normalizes_inputs():
    context = build_ai_context(
        "  Where is Earth?  ",
        " EARTH ",
    )

    assert context.question == "Where is Earth?"
    assert context.object.id == "earth"

def test_build_ai_context_for_moon_does_not_fabricate_scientific_data():
    context = build_ai_context(
        "What is the Moon?",
        "moon",
    )

    assert context.object.id == "moon"
    assert context.object.name == "Moon"
    assert context.object.object_type == "moon"
    assert context.scientific_data is None
    assert context.provenance == ()

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert "context" in capability_ids
    assert "relationships" in capability_ids
    assert "scientific-data" not in capability_ids

def test_build_ai_context_includes_earth_object_graph():
    context = build_ai_context(
        "Where is Earth in the cosmic hierarchy?",
        "earth",
    )

    assert context.object_graph is not None
    assert context.object_graph.object.id == "earth"
    assert context.object_graph.parent.id == "sun"

    assert [
        obj.id
        for obj in context.object_graph.ancestors
    ] == [
        "sun",
        "solar-system",
        "milky-way",
        "universe",
    ]

    assert {
        obj.id
        for obj in context.object_graph.children
    } == {
        "moon",
        "spacecraft:25544",
    }

    relationship_pairs = {
        (
            relationship.relationship_type,
            relationship.target_id,
        )
        for relationship
        in context.object_graph.relationships
    }

    assert ("orbits", "sun") in relationship_pairs
    assert ("contains", "moon") in relationship_pairs
    assert (
        "contains",
        "spacecraft:25544",
    ) in relationship_pairs


def test_build_ai_context_includes_milky_way_object_graph():
    context = build_ai_context(
        "What is in the Milky Way?",
        "milky-way",
    )

    assert context.object_graph is not None
    assert context.object_graph.object.id == "milky-way"
    assert context.object_graph.parent.id == "universe"

    assert {
        obj.id
        for obj in context.object_graph.children
    } >= {
        "solar-system",
        "sirius",
        "proxima-centauri",
        "betelgeuse",
        "vega",
    }


def test_build_ai_context_graph_uses_canonical_objects():
    context = build_ai_context(
        "What does Earth orbit?",
        "earth",
    )

    assert context.object_graph is not None
    assert context.object_graph.object is context.object

    assert (
        context.object_graph.parent.id
        == "sun"
    )


def test_build_ai_context_includes_earth_incoming_relationships():
    context = build_ai_context(
        question="What orbits Earth?",
        object_id="earth",
    )

    incoming = {
        (
            relationship.source_id,
            relationship.relationship_type,
            relationship.target_id,
        )
        for relationship
        in context.object_graph.incoming_relationships
    }

    assert (
        "moon",
        "orbits",
        "earth",
    ) in incoming

    assert (
        "spacecraft:25544",
        "orbits",
        "earth",
    ) in incoming

def test_build_ai_context_question_subject_overrides_page_context():
    context = build_ai_context(
        "When will Apophis approach Earth?",
        "milky-way",
    )

    assert context.object.id == "asteroid:99942"
    assert context.object.name == "Apophis"

    assert context.metadata["reference_body"] == "asteroid:99942"
    assert context.metadata["target_body"] == "earth"

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert "tracking" in capability_ids
    assert "trajectory" in capability_ids
    assert "close-approaches" in capability_ids
