from astrosphere.models.research import ResearchHypothesis
from astrosphere.research.registry import ResearchRegistry


class ResearchHypothesisRegistry:
    def __init__(self, investigation_registry: ResearchRegistry):
        self._investigation_registry = investigation_registry
        self._hypotheses = {}

    def create_hypothesis(
        self,
        hypothesis: ResearchHypothesis,
    ) -> ResearchHypothesis:
        if hypothesis.id in self._hypotheses:
            raise ValueError(
                f"Research hypothesis already exists: {hypothesis.id}"
            )

        self._validate_investigation(hypothesis.investigation_id)

        self._hypotheses[hypothesis.id] = hypothesis
        return hypothesis

    def get_hypothesis(
        self,
        hypothesis_id: str,
    ) -> ResearchHypothesis | None:
        return self._hypotheses.get(hypothesis_id.strip())

    def list_hypotheses(self) -> tuple[ResearchHypothesis, ...]:
        return tuple(self._hypotheses.values())

    def _validate_investigation(
        self,
        investigation_id: str,
    ) -> None:
        if self._investigation_registry.get_investigation(
            investigation_id
        ) is None:
            raise ValueError(
                f"Unknown research investigation: {investigation_id}"
            )
