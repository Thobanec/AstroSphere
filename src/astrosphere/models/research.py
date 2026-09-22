from dataclasses import dataclass

RESEARCH_STATUS_DRAFT = "draft"
RESEARCH_STATUS_ACTIVE = "active"
RESEARCH_STATUS_COMPLETED = "completed"
RESEARCH_STATUS_ARCHIVED = "archived"

RESEARCH_STATUSES = (
    RESEARCH_STATUS_DRAFT,
    RESEARCH_STATUS_ACTIVE,
    RESEARCH_STATUS_COMPLETED,
    RESEARCH_STATUS_ARCHIVED,
)

RESEARCH_EVIDENCE_OBSERVED = "observed"
RESEARCH_EVIDENCE_CALCULATED = "calculated"
RESEARCH_EVIDENCE_DERIVED = "derived"
RESEARCH_EVIDENCE_EXTERNAL_SOURCE = "external_source"

RESEARCH_EVIDENCE_TYPES = (
    RESEARCH_EVIDENCE_OBSERVED,
    RESEARCH_EVIDENCE_CALCULATED,
    RESEARCH_EVIDENCE_DERIVED,
    RESEARCH_EVIDENCE_EXTERNAL_SOURCE,
)


@dataclass(frozen=True)
class ResearchInvestigation:
    id: str
    title: str
    description: str | None = None
    status: str = RESEARCH_STATUS_DRAFT
    owner_id: str | None = None
    participant_ids: tuple[str, ...] = ()
    celestial_object_ids: tuple[str, ...] = ()
    created_at: str | None = None
    updated_at: str | None = None


@dataclass(frozen=True)
class ResearchQuestion:
    id: str
    investigation_id: str
    question: str
    description: str | None = None


@dataclass(frozen=True)
class ResearchHypothesis:
    id: str
    investigation_id: str
    statement: str
    description: str | None = None


@dataclass(frozen=True)
class ResearchEvidence:
    id: str
    investigation_id: str
    observation_id: str
    question_id: str | None = None
    hypothesis_id: str | None = None
    evidence_type: str = RESEARCH_EVIDENCE_OBSERVED
    description: str | None = None
    source_reference: str | None = None
    derived_from_evidence_ids: tuple[str, ...] = ()
