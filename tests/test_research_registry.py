import pytest

from astrosphere.models.research import (
    RESEARCH_STATUS_ACTIVE,
    ResearchInvestigation,
)
from astrosphere.research.registry import (
    ResearchRegistry,
)


def test_research_registry_creates_investigation():
    registry = ResearchRegistry()

    investigation = ResearchInvestigation(
        id="research:earth-orbit",
        title="Earth Orbital Investigation",
        status=RESEARCH_STATUS_ACTIVE,
        celestial_object_ids=(
            "earth",
            "sun",
        ),
    )

    result = registry.create_investigation(
        investigation
    )

    assert result == investigation


def test_research_registry_retrieves_investigation():
    registry = ResearchRegistry()

    investigation = ResearchInvestigation(
        id="research:001",
        title="Earth Investigation",
        celestial_object_ids=("earth",),
    )

    registry.create_investigation(
        investigation
    )

    result = registry.get_investigation(
        "research:001"
    )

    assert result == investigation


def test_research_registry_lists_investigations():
    registry = ResearchRegistry()

    first = ResearchInvestigation(
        id="research:001",
        title="Earth Investigation",
        celestial_object_ids=("earth",),
    )

    second = ResearchInvestigation(
        id="research:002",
        title="Sun Investigation",
        celestial_object_ids=("sun",),
    )

    registry.create_investigation(first)
    registry.create_investigation(second)

    result = registry.list_investigations()

    assert result == (
        first,
        second,
    )


def test_research_registry_validates_celestial_objects():
    registry = ResearchRegistry()

    investigation = ResearchInvestigation(
        id="research:invalid",
        title="Invalid Investigation",
        celestial_object_ids=(
            "does-not-exist",
        ),
    )

    with pytest.raises(
        ValueError,
        match="Unknown celestial object",
    ):
        registry.create_investigation(
            investigation
        )


def test_research_registry_rejects_duplicate_ids():
    registry = ResearchRegistry()

    investigation = ResearchInvestigation(
        id="research:duplicate",
        title="First Investigation",
    )

    registry.create_investigation(
        investigation
    )

    duplicate = ResearchInvestigation(
        id="research:duplicate",
        title="Second Investigation",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        registry.create_investigation(
            duplicate
        )


def test_research_registry_returns_none_for_unknown_id():
    registry = ResearchRegistry()

    assert (
        registry.get_investigation(
            "research:missing"
        )
        is None
    )
