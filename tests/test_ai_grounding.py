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

    assert "CelesTrak" in provenance_names


def test_build_ai_context_for_sun_does_not_fabricate_scientific_data():
    context = build_ai_context(
        "What is the Sun?",
        "sun",
    )

    assert context.object.id == "sun"
    assert context.object.name == "Sun"
    assert context.scientific_data is None
    assert context.provenance == ()

    capability_ids = {
        capability.id
        for capability in context.capabilities
    }

    assert capability_ids == {
        "context",
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
