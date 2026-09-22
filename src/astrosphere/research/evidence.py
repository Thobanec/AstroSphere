from astrosphere.models.scientific import ScientificProvenance
from astrosphere.models.research import (
    RESEARCH_EVIDENCE_TYPES,
    ResearchEvidence,
)
from astrosphere.research.hypotheses import ResearchHypothesisRegistry
from astrosphere.research.questions import ResearchQuestionRegistry
from astrosphere.research.registry import ResearchRegistry


class ResearchEvidenceRegistry:
    def __init__(
        self,
        investigation_registry: ResearchRegistry,
        question_registry: ResearchQuestionRegistry | None = None,
        hypothesis_registry: ResearchHypothesisRegistry | None = None,
        observation_resolver=None,
    ):
        self._investigation_registry = investigation_registry
        self._question_registry = question_registry
        self._hypothesis_registry = hypothesis_registry
        self._observation_resolver = observation_resolver
        self._evidence = {}

    def create_evidence(
        self,
        evidence: ResearchEvidence,
    ) -> ResearchEvidence:
        if evidence.id in self._evidence:
            raise ValueError(
                f"Research evidence already exists: {evidence.id}"
            )

        self._validate_evidence_type(
            evidence.evidence_type
        )

        self._validate_investigation(
            evidence.investigation_id
        )

        self._validate_question(
            evidence.question_id,
            evidence.investigation_id,
        )

        self._validate_hypothesis(
            evidence.hypothesis_id,
            evidence.investigation_id,
        )

        self._validate_source_reference(evidence)

        self._validate_derived_evidence(evidence)

        self._validate_observation(evidence)

        self._evidence[evidence.id] = evidence

        return evidence

    def get_evidence(
        self,
        evidence_id: str,
    ) -> ResearchEvidence | None:
        return self._evidence.get(
            evidence_id.strip()
        )

    def resolve_evidence_provenance(
        self,
        evidence_id: str,
        provenance_resolver,
    ) -> ScientificProvenance:
        evidence = self.get_evidence(evidence_id)

        if evidence is None:
            raise ValueError(
                f"Unknown research evidence: {evidence_id}"
            )

        if provenance_resolver is None:
            raise ValueError(
                "A provenance resolver is required"
            )

        try:
            provenance = provenance_resolver(
                evidence.observation_id
            )
        except (ValueError, LookupError) as exc:
            raise ValueError(
                "Research evidence references an observation "
                f"with unresolvable provenance: "
                f"{evidence.observation_id}"
            ) from exc

        if provenance is None:
            raise ValueError(
                "Research evidence observation does not contain provenance: "
                f"{evidence.observation_id}"
            )

        return provenance
    def list_evidence(
        self,
    ) -> tuple[ResearchEvidence, ...]:
        return tuple(self._evidence.values())

    @staticmethod
    def _validate_evidence_type(
        evidence_type: str,
    ) -> None:
        if evidence_type not in RESEARCH_EVIDENCE_TYPES:
            raise ValueError(
                f"Unsupported research evidence type: "
                f"{evidence_type}"
            )

    def _validate_investigation(
        self,
        investigation_id: str,
    ) -> None:
        if (
            self._investigation_registry.get_investigation(
                investigation_id
            )
            is None
        ):
            raise ValueError(
                f"Unknown research investigation: "
                f"{investigation_id}"
            )

    def _validate_question(
        self,
        question_id: str | None,
        investigation_id: str,
    ) -> None:
        if question_id is None:
            return

        if self._question_registry is None:
            raise ValueError(
                "Question registry is required when "
                "question_id is supplied"
            )

        question = self._question_registry.get_question(
            question_id
        )

        if question is None:
            raise ValueError(
                f"Unknown research question: {question_id}"
            )

        if question.investigation_id != investigation_id:
            raise ValueError(
                "Research question belongs to a different "
                "investigation"
            )

    def _validate_hypothesis(
        self,
        hypothesis_id: str | None,
        investigation_id: str,
    ) -> None:
        if hypothesis_id is None:
            return

        if self._hypothesis_registry is None:
            raise ValueError(
                "Hypothesis registry is required when "
                "hypothesis_id is supplied"
            )

        hypothesis = (
            self._hypothesis_registry.get_hypothesis(
                hypothesis_id
            )
        )

        if hypothesis is None:
            raise ValueError(
                f"Unknown research hypothesis: "
                f"{hypothesis_id}"
            )

        if hypothesis.investigation_id != investigation_id:
            raise ValueError(
                "Research hypothesis belongs to a different "
                "investigation"
            )

    @staticmethod
    def _validate_source_reference(
        evidence: ResearchEvidence,
    ) -> None:
        if (
            evidence.evidence_type
            == "external_source"
            and not evidence.source_reference
        ):
            raise ValueError(
                "External-source evidence requires "
                "a source_reference"
            )

    def _validate_derived_evidence(
        self,
        evidence: ResearchEvidence,
    ) -> None:
        if evidence.evidence_type != "derived":
            if evidence.derived_from_evidence_ids:
                raise ValueError(
                    "Only derived evidence may reference "
                    "source evidence"
                )
            return

        for evidence_id in (
            evidence.derived_from_evidence_ids
        ):
            if evidence_id == evidence.id:
                raise ValueError(
                    "Research evidence cannot derive "
                    "from itself"
                )

            if self.get_evidence(evidence_id) is None:
                raise ValueError(
                    f"Unknown source research evidence: "
                    f"{evidence_id}"
                )

    def _validate_observation(
        self,
        evidence: ResearchEvidence,
    ) -> None:
        if self._observation_resolver is None:
            return

        if not evidence.observation_id:
            raise ValueError(
                "Research evidence must contain an "
                "observation_id"
            )

        try:
            self._observation_resolver(
                evidence.observation_id
            )
        except (ValueError, LookupError) as exc:
            raise ValueError(
                "Research evidence references an "
                "unresolvable observation: "
                f"{evidence.observation_id}"
            ) from exc
