from astrosphere.models.celestial_registry import (
    get_celestial_object,
)
from astrosphere.models.research import (
    ResearchInvestigation,
)


class ResearchRegistry:
    def __init__(self):
        self._investigations = {}

    def create_investigation(
        self,
        investigation: ResearchInvestigation,
    ) -> ResearchInvestigation:
        if investigation.id in self._investigations:
            raise ValueError(
                f"Research investigation already exists: "
                f"{investigation.id}"
            )

        self._validate_celestial_objects(
            investigation
        )

        self._investigations[investigation.id] = (
            investigation
        )

        return investigation

    def get_investigation(
        self,
        investigation_id: str,
    ) -> ResearchInvestigation | None:
        return self._investigations.get(
            investigation_id.strip()
        )

    def list_investigations(
        self,
    ) -> tuple[ResearchInvestigation, ...]:
        return tuple(
            self._investigations.values()
        )

    @staticmethod
    def _validate_celestial_objects(
        investigation: ResearchInvestigation,
    ) -> None:
        for object_id in investigation.celestial_object_ids:
            if get_celestial_object(object_id) is None:
                raise ValueError(
                    "Unknown celestial object: "
                    f"{object_id}"
                )
