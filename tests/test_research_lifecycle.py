import pytest

from astrosphere.models.research import (
    RESEARCH_STATUS_ACTIVE,
    RESEARCH_STATUS_ARCHIVED,
    RESEARCH_STATUS_COMPLETED,
    RESEARCH_STATUS_DRAFT,
    ResearchInvestigation,
)
from astrosphere.research.lifecycle import (
    ResearchLifecycle,
)


def make_investigation(
    status=RESEARCH_STATUS_DRAFT,
):
    return ResearchInvestigation(
        id="research:lifecycle",
        title="Lifecycle Investigation",
        status=status,
        celestial_object_ids=("earth",),
    )


def test_draft_can_be_activated():
    investigation = make_investigation()

    result = ResearchLifecycle.activate(
        investigation
    )

    assert investigation.status == RESEARCH_STATUS_DRAFT
    assert result.status == RESEARCH_STATUS_ACTIVE
    assert result.id == investigation.id


def test_active_can_be_completed():
    investigation = make_investigation(
        RESEARCH_STATUS_ACTIVE
    )

    result = ResearchLifecycle.complete(
        investigation
    )

    assert result.status == RESEARCH_STATUS_COMPLETED


def test_completed_can_be_archived():
    investigation = make_investigation(
        RESEARCH_STATUS_COMPLETED
    )

    result = ResearchLifecycle.archive(
        investigation
    )

    assert result.status == RESEARCH_STATUS_ARCHIVED


def test_draft_can_be_archived():
    investigation = make_investigation()

    result = ResearchLifecycle.archive(
        investigation
    )

    assert result.status == RESEARCH_STATUS_ARCHIVED


def test_active_can_be_archived():
    investigation = make_investigation(
        RESEARCH_STATUS_ACTIVE
    )

    result = ResearchLifecycle.archive(
        investigation
    )

    assert result.status == RESEARCH_STATUS_ARCHIVED


def test_invalid_completed_to_active_transition_is_rejected():
    investigation = make_investigation(
        RESEARCH_STATUS_COMPLETED
    )

    with pytest.raises(
        ValueError,
        match="Invalid research lifecycle transition",
    ):
        ResearchLifecycle.activate(
            investigation
        )


def test_invalid_archived_to_active_transition_is_rejected():
    investigation = make_investigation(
        RESEARCH_STATUS_ARCHIVED
    )

    with pytest.raises(
        ValueError,
        match="Invalid research lifecycle transition",
    ):
        ResearchLifecycle.activate(
            investigation
        )


def test_archived_investigation_cannot_be_completed():
    investigation = make_investigation(
        RESEARCH_STATUS_ARCHIVED
    )

    with pytest.raises(
        ValueError,
        match="Invalid research lifecycle transition",
    ):
        ResearchLifecycle.complete(
            investigation
        )


def test_unknown_status_is_rejected():
    investigation = make_investigation()

    with pytest.raises(
        ValueError,
        match="Unknown research status",
    ):
        ResearchLifecycle.transition(
            investigation,
            "unknown",
        )


def test_same_status_returns_equivalent_investigation():
    investigation = make_investigation()

    result = ResearchLifecycle.transition(
        investigation,
        RESEARCH_STATUS_DRAFT,
    )

    assert result == investigation
