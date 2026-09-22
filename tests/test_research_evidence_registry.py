import pytest

from astrosphere.models.research import (
    RESEARCH_EVIDENCE_CALCULATED,
    RESEARCH_EVIDENCE_DERIVED,
    RESEARCH_EVIDENCE_EXTERNAL_SOURCE,
    RESEARCH_EVIDENCE_OBSERVED,
    ResearchEvidence,
    ResearchHypothesis,
    ResearchInvestigation,
    ResearchQuestion,
)
from astrosphere.research.evidence import ResearchEvidenceRegistry
from astrosphere.research.hypotheses import ResearchHypothesisRegistry
from astrosphere.research.questions import ResearchQuestionRegistry
from astrosphere.research.registry import ResearchRegistry


def make_registries():
    investigations = ResearchRegistry()

    investigations.create_investigation(
        ResearchInvestigation(
            id="research-001",
            title="Earth Observation Study",
            celestial_object_ids=("earth",),
        )
    )

    investigations.create_investigation(
        ResearchInvestigation(
            id="research-002",
            title="Second Earth Study",
            celestial_object_ids=("earth",),
        )
    )

    questions = ResearchQuestionRegistry(investigations)

    questions.create_question(
        ResearchQuestion(
            id="question-001",
            investigation_id="research-001",
            question="How does Earth's position change over time?",
        )
    )

    questions.create_question(
        ResearchQuestion(
            id="question-002",
            investigation_id="research-002",
            question="How does Earth's velocity change?",
        )
    )

    hypotheses = ResearchHypothesisRegistry(investigations)

    hypotheses.create_hypothesis(
        ResearchHypothesis(
            id="hypothesis-001",
            investigation_id="research-001",
            statement="Earth follows the expected orbital model.",
        )
    )

    hypotheses.create_hypothesis(
        ResearchHypothesis(
            id="hypothesis-002",
            investigation_id="research-002",
            statement="Earth's velocity follows the expected model.",
        )
    )

    evidence = ResearchEvidenceRegistry(
        investigations,
        questions,
        hypotheses,
    )

    return investigations, questions, hypotheses, evidence


def test_create_evidence():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        question_id="question-001",
        hypothesis_id="hypothesis-001",
        evidence_type=RESEARCH_EVIDENCE_OBSERVED,
        description="Observed Earth position.",
    )

    result = registry.create_evidence(evidence)

    assert result == evidence


def test_get_evidence():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
    )

    registry.create_evidence(evidence)

    assert registry.get_evidence("evidence-001") == evidence


def test_get_unknown_evidence_returns_none():
    _, _, _, registry = make_registries()

    assert registry.get_evidence("missing") is None


def test_list_evidence():
    _, _, _, registry = make_registries()

    evidence_one = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
    )

    evidence_two = ResearchEvidence(
        id="evidence-002",
        investigation_id="research-001",
        observation_id="observation-002",
    )

    registry.create_evidence(evidence_one)
    registry.create_evidence(evidence_two)

    assert registry.list_evidence() == (
        evidence_one,
        evidence_two,
    )


def test_evidence_requires_existing_investigation():
    investigations = ResearchRegistry()
    registry = ResearchEvidenceRegistry(investigations)

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="missing-research",
        observation_id="observation-001",
    )

    with pytest.raises(
        ValueError,
        match="Unknown research investigation",
    ):
        registry.create_evidence(evidence)


def test_evidence_question_must_exist():
    investigations = ResearchRegistry()

    investigations.create_investigation(
        ResearchInvestigation(
            id="research-001",
            title="Earth Study",
            celestial_object_ids=("earth",),
        )
    )

    questions = ResearchQuestionRegistry(investigations)
    hypotheses = ResearchHypothesisRegistry(investigations)

    registry = ResearchEvidenceRegistry(
        investigations,
        questions,
        hypotheses,
    )

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        question_id="missing-question",
    )

    with pytest.raises(
        ValueError,
        match="Unknown research question",
    ):
        registry.create_evidence(evidence)


def test_evidence_hypothesis_must_exist():
    investigations = ResearchRegistry()

    investigations.create_investigation(
        ResearchInvestigation(
            id="research-001",
            title="Earth Study",
            celestial_object_ids=("earth",),
        )
    )

    questions = ResearchQuestionRegistry(investigations)
    hypotheses = ResearchHypothesisRegistry(investigations)

    registry = ResearchEvidenceRegistry(
        investigations,
        questions,
        hypotheses,
    )

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        hypothesis_id="missing-hypothesis",
    )

    with pytest.raises(
        ValueError,
        match="Unknown research hypothesis",
    ):
        registry.create_evidence(evidence)


def test_question_must_belong_to_same_investigation():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        question_id="question-002",
    )

    with pytest.raises(
        ValueError,
        match="belongs to a different investigation",
    ):
        registry.create_evidence(evidence)


def test_hypothesis_must_belong_to_same_investigation():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        hypothesis_id="hypothesis-002",
    )

    with pytest.raises(
        ValueError,
        match="belongs to a different investigation",
    ):
        registry.create_evidence(evidence)


def test_invalid_evidence_type_is_rejected():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        evidence_type="speculation",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported research evidence type",
    ):
        registry.create_evidence(evidence)


def test_external_source_requires_source_reference():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        evidence_type=RESEARCH_EVIDENCE_EXTERNAL_SOURCE,
    )

    with pytest.raises(
        ValueError,
        match="requires a source_reference",
    ):
        registry.create_evidence(evidence)


def test_external_source_accepts_source_reference():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        evidence_type=RESEARCH_EVIDENCE_EXTERNAL_SOURCE,
        source_reference="NASA/JPL",
    )

    assert registry.create_evidence(evidence) == evidence


def test_calculated_evidence_is_supported():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="calculation-001",
        evidence_type=RESEARCH_EVIDENCE_CALCULATED,
    )

    assert registry.create_evidence(evidence) == evidence


def test_derived_evidence_requires_existing_source():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-002",
        investigation_id="research-001",
        observation_id="derived-001",
        evidence_type=RESEARCH_EVIDENCE_DERIVED,
        derived_from_evidence_ids=("missing-evidence",),
    )

    with pytest.raises(
        ValueError,
        match="Unknown source research evidence",
    ):
        registry.create_evidence(evidence)


def test_derived_evidence_can_reference_existing_evidence():
    _, _, _, registry = make_registries()

    source = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
        evidence_type=RESEARCH_EVIDENCE_OBSERVED,
    )

    registry.create_evidence(source)

    derived = ResearchEvidence(
        id="evidence-002",
        investigation_id="research-001",
        observation_id="derived-001",
        evidence_type=RESEARCH_EVIDENCE_DERIVED,
        derived_from_evidence_ids=("evidence-001",),
    )

    assert registry.create_evidence(derived) == derived


def test_derived_evidence_cannot_reference_itself():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="derived-001",
        evidence_type=RESEARCH_EVIDENCE_DERIVED,
        derived_from_evidence_ids=("evidence-001",),
    )

    with pytest.raises(
        ValueError,
        match="cannot derive from itself",
    ):
        registry.create_evidence(evidence)


def test_non_derived_evidence_cannot_have_source_evidence():
    _, _, _, registry = make_registries()

    source = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
    )

    registry.create_evidence(source)

    evidence = ResearchEvidence(
        id="evidence-002",
        investigation_id="research-001",
        observation_id="observation-002",
        evidence_type=RESEARCH_EVIDENCE_OBSERVED,
        derived_from_evidence_ids=("evidence-001",),
    )

    with pytest.raises(
        ValueError,
        match="Only derived evidence",
    ):
        registry.create_evidence(evidence)


def test_duplicate_evidence_id_is_rejected():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
    )

    registry.create_evidence(evidence)

    duplicate = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-002",
    )

    with pytest.raises(
        ValueError,
        match="Research evidence already exists",
    ):
        registry.create_evidence(duplicate)


def test_evidence_can_exist_without_question_or_hypothesis():
    _, _, _, registry = make_registries()

    evidence = ResearchEvidence(
        id="evidence-001",
        investigation_id="research-001",
        observation_id="observation-001",
    )

    result = registry.create_evidence(evidence)

    assert result.question_id is None
    assert result.hypothesis_id is None

def test_evidence_accepts_resolvable_observation():
    investigation_registry, _, _, _ = make_registries()

    def resolve_observation(observation_id):
        assert observation_id == (
            "scientific:earth:"
            "2026-09-22T06:00:00+00:00:JPL DE440S"
        )
        return object()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
        observation_resolver=resolve_observation,
    )

    evidence = ResearchEvidence(
        id="evidence-observation-valid",
        investigation_id="research-001",
        observation_id=(
            "scientific:earth:"
            "2026-09-22T06:00:00+00:00:JPL DE440S"
        ),
    )

    created = registry.create_evidence(evidence)

    assert created == evidence


def test_evidence_rejects_unresolvable_observation():
    investigation_registry, _, _, _ = make_registries()

    def resolve_observation(observation_id):
        raise ValueError(
            "Invalid scientific observation"
        )

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
        observation_resolver=resolve_observation,
    )

    evidence = ResearchEvidence(
        id="evidence-observation-invalid",
        investigation_id="research-001",
        observation_id="scientific:invalid",
    )

    try:
        registry.create_evidence(evidence)
    except ValueError as exc:
        assert str(exc) == (
            "Research evidence references an "
            "unresolvable observation: scientific:invalid"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_evidence_requires_observation_id_when_resolver_is_configured():
    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
        observation_resolver=lambda observation_id: object(),
    )

    evidence = ResearchEvidence(
        id="evidence-observation-missing",
        investigation_id="research-001",
        observation_id="",
    )

    try:
        registry.create_evidence(evidence)
    except ValueError as exc:
        assert str(exc) == (
            "Research evidence must contain an "
            "observation_id"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_evidence_without_resolver_preserves_existing_behavior():
    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
    )

    evidence = ResearchEvidence(
        id="evidence-no-resolver",
        investigation_id="research-001",
        observation_id="arbitrary-observation-id",
    )

    created = registry.create_evidence(evidence)

    assert created == evidence

def test_evidence_resolves_real_scientific_observation():
    from astrosphere.research.scientific import resolve_observation_id

    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
        observation_resolver=resolve_observation_id,
    )

    evidence = ResearchEvidence(
        id="evidence-real-scientific-observation",
        investigation_id="research-001",
        observation_id=(
            "scientific:earth:"
            "2026-09-22T06:00:00+00:00:JPL DE440S"
        ),
    )

    created = registry.create_evidence(evidence)

    assert created == evidence


def test_evidence_resolves_scientific_provenance():
    from astrosphere.research.scientific import (
        resolve_observation_provenance,
    )

    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
    )

    evidence = ResearchEvidence(
        id="evidence-provenance-trace",
        investigation_id="research-001",
        observation_id=(
            "scientific:earth:"
            "2026-09-22T06:00:00+00:00:JPL DE440S"
        ),
    )

    registry.create_evidence(evidence)

    provenance = registry.resolve_evidence_provenance(
        evidence.id,
        resolve_observation_provenance,
    )

    assert provenance.reference_frames == ("ICRF",)

    source_names = tuple(
        source.name
        for source in provenance.sources
    )

    assert "JPL DE440S" in source_names
    assert "JPL Planetary Physical Parameters" in source_names


def test_evidence_provenance_rejects_unknown_evidence():
    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
    )

    try:
        registry.resolve_evidence_provenance(
            "missing-evidence",
            lambda observation_id: object(),
        )
    except ValueError as exc:
        assert str(exc) == (
            "Unknown research evidence: missing-evidence"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_evidence_provenance_requires_resolver():
    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
    )

    evidence = ResearchEvidence(
        id="evidence-provenance-no-resolver",
        investigation_id="research-001",
        observation_id="observation-001",
    )

    registry.create_evidence(evidence)

    try:
        registry.resolve_evidence_provenance(
            evidence.id,
            None,
        )
    except ValueError as exc:
        assert str(exc) == (
            "A provenance resolver is required"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_evidence_provenance_rejects_unresolvable_observation():
    investigation_registry, _, _, _ = make_registries()

    registry = ResearchEvidenceRegistry(
        investigation_registry=investigation_registry,
    )

    evidence = ResearchEvidence(
        id="evidence-provenance-invalid",
        investigation_id="research-001",
        observation_id="scientific:invalid",
    )

    registry.create_evidence(evidence)

    def resolver(observation_id):
        raise ValueError("Invalid observation")

    try:
        registry.resolve_evidence_provenance(
            evidence.id,
            resolver,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Research evidence references an observation "
            "with unresolvable provenance: "
            "scientific:invalid"
        )
    else:
        raise AssertionError("Expected ValueError")
