from astrosphere.ai.entity_resolution import (
    resolve_object_or_default,
)


def test_named_question_entity_overrides_page_context():
    result = resolve_object_or_default(
        "Tell me about Mars.",
        explicit_object_id="milky-way",
    )

    assert result.reference_object_id == "mars"
    assert result.target_object_id is None


def test_two_named_entities_resolve_reference_and_target():
    result = resolve_object_or_default(
        "How far is Earth from Mars?",
        explicit_object_id="milky-way",
    )

    assert result.reference_object_id == "earth"
    assert result.target_object_id == "mars"


def test_contextual_pronoun_preserves_selected_subject():
    result = resolve_object_or_default(
        "When will it approach Earth?",
        explicit_object_id="asteroid:99942",
    )

    assert result.reference_object_id == "asteroid:99942"
    assert result.target_object_id == "earth"


def test_explicit_subject_overrides_page_context():
    result = resolve_object_or_default(
        "When will Apophis approach Earth?",
        explicit_object_id="milky-way",
    )

    assert result.reference_object_id == "asteroid:99942"
    assert result.target_object_id == "earth"


def test_contextual_pronoun_without_target_preserves_subject():
    result = resolve_object_or_default(
        "How fast is it moving?",
        explicit_object_id="asteroid:99942",
    )

    assert result.reference_object_id == "asteroid:99942"
    assert result.target_object_id is None
