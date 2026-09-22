import pytest

from astrosphere.models.research import (
    ResearchInvestigation,
    ResearchQuestion,
)
from astrosphere.research.questions import ResearchQuestionRegistry
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


def test_create_question():
    investigations = make_investigation_registry()
    registry = ResearchQuestionRegistry(investigations)

    question = ResearchQuestion(
        id="question-001",
        investigation_id="research-001",
        question="How does Earth's position change over time?",
    )

    result = registry.create_question(question)

    assert result == question


def test_get_question():
    investigations = make_investigation_registry()
    registry = ResearchQuestionRegistry(investigations)

    question = ResearchQuestion(
        id="question-001",
        investigation_id="research-001",
        question="How does Earth's position change over time?",
    )

    registry.create_question(question)

    assert registry.get_question("question-001") == question


def test_get_unknown_question_returns_none():
    investigations = make_investigation_registry()
    registry = ResearchQuestionRegistry(investigations)

    assert registry.get_question("missing") is None


def test_list_questions():
    investigations = make_investigation_registry()
    registry = ResearchQuestionRegistry(investigations)

    question_one = ResearchQuestion(
        id="question-001",
        investigation_id="research-001",
        question="Question one?",
    )

    question_two = ResearchQuestion(
        id="question-002",
        investigation_id="research-001",
        question="Question two?",
    )

    registry.create_question(question_one)
    registry.create_question(question_two)

    assert registry.list_questions() == (
        question_one,
        question_two,
    )


def test_question_requires_existing_investigation():
    investigations = ResearchRegistry()
    registry = ResearchQuestionRegistry(investigations)

    question = ResearchQuestion(
        id="question-001",
        investigation_id="missing-research",
        question="Does this investigation exist?",
    )

    with pytest.raises(
        ValueError,
        match="Unknown research investigation",
    ):
        registry.create_question(question)


def test_duplicate_question_id_is_rejected():
    investigations = make_investigation_registry()
    registry = ResearchQuestionRegistry(investigations)

    question = ResearchQuestion(
        id="question-001",
        investigation_id="research-001",
        question="Original question?",
    )

    registry.create_question(question)

    duplicate = ResearchQuestion(
        id="question-001",
        investigation_id="research-001",
        question="Duplicate question?",
    )

    with pytest.raises(
        ValueError,
        match="Research question already exists",
    ):
        registry.create_question(duplicate)
