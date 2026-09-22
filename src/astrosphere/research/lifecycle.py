from dataclasses import replace

from astrosphere.models.research import (
    RESEARCH_STATUS_ACTIVE,
    RESEARCH_STATUS_ARCHIVED,
    RESEARCH_STATUS_COMPLETED,
    RESEARCH_STATUS_DRAFT,
    ResearchInvestigation,
)


_ALLOWED_TRANSITIONS = {
    RESEARCH_STATUS_DRAFT: {
        RESEARCH_STATUS_ACTIVE,
        RESEARCH_STATUS_ARCHIVED,
    },
    RESEARCH_STATUS_ACTIVE: {
        RESEARCH_STATUS_COMPLETED,
        RESEARCH_STATUS_ARCHIVED,
    },
    RESEARCH_STATUS_COMPLETED: {
        RESEARCH_STATUS_ARCHIVED,
    },
    RESEARCH_STATUS_ARCHIVED: set(),
}


class ResearchLifecycle:
    @staticmethod
    def transition(
        investigation: ResearchInvestigation,
        target_status: str,
    ) -> ResearchInvestigation:
        if target_status not in {
            RESEARCH_STATUS_DRAFT,
            RESEARCH_STATUS_ACTIVE,
            RESEARCH_STATUS_COMPLETED,
            RESEARCH_STATUS_ARCHIVED,
        }:
            raise ValueError(
                f"Unknown research status: {target_status}"
            )

        current_status = investigation.status

        if target_status == current_status:
            return investigation

        allowed_statuses = _ALLOWED_TRANSITIONS[
            current_status
        ]

        if target_status not in allowed_statuses:
            raise ValueError(
                "Invalid research lifecycle transition: "
                f"{current_status} -> {target_status}"
            )

        return replace(
            investigation,
            status=target_status,
        )

    @staticmethod
    def activate(
        investigation: ResearchInvestigation,
    ) -> ResearchInvestigation:
        return ResearchLifecycle.transition(
            investigation,
            RESEARCH_STATUS_ACTIVE,
        )

    @staticmethod
    def complete(
        investigation: ResearchInvestigation,
    ) -> ResearchInvestigation:
        return ResearchLifecycle.transition(
            investigation,
            RESEARCH_STATUS_COMPLETED,
        )

    @staticmethod
    def archive(
        investigation: ResearchInvestigation,
    ) -> ResearchInvestigation:
        return ResearchLifecycle.transition(
            investigation,
            RESEARCH_STATUS_ARCHIVED,
        )
