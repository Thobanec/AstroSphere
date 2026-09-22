from astrosphere.models.research import (
    RESEARCH_STATUS_ACTIVE,
    RESEARCH_STATUS_ARCHIVED,
    RESEARCH_STATUS_COMPLETED,
    RESEARCH_STATUS_DRAFT,
    RESEARCH_STATUSES,
    ResearchInvestigation,
)


def test_research_investigation_defaults():
    investigation = ResearchInvestigation(
        id="research:001",
        title="Earth Orbital Investigation",
    )

    assert investigation.id == "research:001"
    assert investigation.title == "Earth Orbital Investigation"
    assert investigation.description is None
    assert investigation.status == RESEARCH_STATUS_DRAFT
    assert investigation.owner_id is None
    assert investigation.participant_ids == ()
    assert investigation.celestial_object_ids == ()
    assert investigation.created_at is None
    assert investigation.updated_at is None


def test_research_investigation_supports_canonical_celestial_object_ids():
    investigation = ResearchInvestigation(
        id="research:002",
        title="Earth-Sun Investigation",
        description="Study Earth's motion around the Sun.",
        status=RESEARCH_STATUS_ACTIVE,
        owner_id="user:001",
        participant_ids=("user:002", "user:003"),
        celestial_object_ids=("earth", "sun"),
        created_at="2026-09-22T00:00:00+00:00",
        updated_at="2026-09-22T01:00:00+00:00",
    )

    assert investigation.status == RESEARCH_STATUS_ACTIVE
    assert investigation.owner_id == "user:001"
    assert investigation.participant_ids == (
        "user:002",
        "user:003",
    )
    assert investigation.celestial_object_ids == (
        "earth",
        "sun",
    )


def test_research_statuses_are_explicit():
    assert RESEARCH_STATUSES == (
        RESEARCH_STATUS_DRAFT,
        RESEARCH_STATUS_ACTIVE,
        RESEARCH_STATUS_COMPLETED,
        RESEARCH_STATUS_ARCHIVED,
    )


def test_research_investigation_is_immutable():
    investigation = ResearchInvestigation(
        id="research:003",
        title="Test Investigation",
    )

    try:
        investigation.title = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "ResearchInvestigation should be immutable."
        )
from astrosphere.models.research import (
    ResearchHypothesis,
    ResearchQuestion,
)


def test_research_question_references_investigation():
    question = ResearchQuestion(
        id="question:001",
        investigation_id="research:earth-orbit",
        question="How does Earth's distance from the Sun vary?",
    )

    assert question.id == "question:001"
    assert question.investigation_id == "research:earth-orbit"
    assert (
        question.question
        == "How does Earth's distance from the Sun vary?"
    )
    assert question.description is None


def test_research_question_supports_description():
    question = ResearchQuestion(
        id="question:002",
        investigation_id="research:earth-orbit",
        question="How does Earth's orbital distance vary?",
        description="Measure the variation over a defined period.",
    )

    assert question.description == (
        "Measure the variation over a defined period."
    )


def test_research_hypothesis_references_investigation():
    hypothesis = ResearchHypothesis(
        id="hypothesis:001",
        investigation_id="research:earth-orbit",
        statement=(
            "Earth's distance from the Sun varies "
            "throughout its orbit."
        ),
    )

    assert hypothesis.id == "hypothesis:001"
    assert hypothesis.investigation_id == "research:earth-orbit"
    assert hypothesis.statement == (
        "Earth's distance from the Sun varies "
        "throughout its orbit."
    )
    assert hypothesis.description is None


def test_research_hypothesis_supports_description():
    hypothesis = ResearchHypothesis(
        id="hypothesis:002",
        investigation_id="research:earth-orbit",
        statement="The measured orbital distance will vary.",
        description="Expected outcome before analysis.",
    )

    assert hypothesis.description == (
        "Expected outcome before analysis."
    )


def test_research_question_is_immutable():
    question = ResearchQuestion(
        id="question:003",
        investigation_id="research:test",
        question="Test question",
    )

    try:
        question.question = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "ResearchQuestion should be immutable."
        )


def test_research_hypothesis_is_immutable():
    hypothesis = ResearchHypothesis(
        id="hypothesis:003",
        investigation_id="research:test",
        statement="Test hypothesis",
    )

    try:
        hypothesis.statement = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "ResearchHypothesis should be immutable."
        )
