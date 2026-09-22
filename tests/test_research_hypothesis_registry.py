import pytest

from astrosphere.models.research import (
    ResearchHypothesis,
    ResearchInvestigation,
)
from astrosphere.research.hypotheses import ResearchHypothesisRegistry
from astrosphere.research.registry import ResearchRegistry


def make_investigation_registry():
    registry = ResearchRegistry()

    registry.create_investigation(
        ResearchInvestigation(
            id="research-001",
            title="Earth Observation Study",
            celestial_object_ids=("earth",),
        )
    )

    return registry


def test_create_hypothesis():
    investigations = make_investigation_registry()
    registry = ResearchHypothesisRegistry(investigations)

    hypothesis = ResearchHypothesis(
        id="hypothesis-001",
        investigation_id="research-001",
        statement="Earth's position follows the expected orbital model.",
    )

    result = registry.create_hypothesis(hypothesis)

    assert result == hypothesis


def test_get_hypothesis():
    investigations = make_investigation_registry()
    registry = ResearchHypothesisRegistry(investigations)

    hypothesis = ResearchHypothesis(
        id="hypothesis-001",
        investigation_id="research-001",
        statement="Earth follows the expected orbital model.",
    )

    registry.create_hypothesis(hypothesis)

    assert registry.get_hypothesis("hypothesis-001") == hypothesis


def test_get_unknown_hypothesis_returns_none():
    investigations = make_investigation_registry()
    registry = ResearchHypothesisRegistry(investigations)

    assert registry.get_hypothesis("missing") is None


def test_list_hypotheses():
    investigations = make_investigation_registry()
    registry = ResearchHypothesisRegistry(investigations)

    hypothesis_one = ResearchHypothesis(
        id="hypothesis-001",
        investigation_id="research-001",
        statement="Hypothesis one.",
    )

    hypothesis_two = ResearchHypothesis(
        id="hypothesis-002",
        investigation_id="research-001",
        statement="Hypothesis two.",
    )

    registry.create_hypothesis(hypothesis_one)
    registry.create_hypothesis(hypothesis_two)

    assert registry.list_hypotheses() == (
        hypothesis_one,
        hypothesis_two,
    )


def test_hypothesis_requires_existing_investigation():
    investigations = ResearchRegistry()
    registry = ResearchHypothesisRegistry(investigations)

    hypothesis = ResearchHypothesis(
        id="hypothesis-001",
        investigation_id="missing-research",
        statement="This investigation does not exist.",
    )

    with pytest.raises(
        ValueError,
        match="Unknown research investigation",
    ):
        registry.create_hypothesis(hypothesis)


def test_duplicate_hypothesis_id_is_rejected():
    investigations = make_investigation_registry()
    registry = ResearchHypothesisRegistry(investigations)

    hypothesis = ResearchHypothesis(
        id="hypothesis-001",
        investigation_id="research-001",
        statement="Original hypothesis.",
    )

    registry.create_hypothesis(hypothesis)

    duplicate = ResearchHypothesis(
        id="hypothesis-001",
        investigation_id="research-001",
        statement="Duplicate hypothesis.",
    )

    with pytest.raises(
        ValueError,
        match="Research hypothesis already exists",
    ):
        registry.create_hypothesis(duplicate)
