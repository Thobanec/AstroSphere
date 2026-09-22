from dataclasses import dataclass
from datetime import datetime

from astrosphere.models.celestial_registry import get_celestial_object
from astrosphere.models.scientific import ScientificData, ScientificProvenance
from astrosphere.scientific.service import get_scientific_data


@dataclass(frozen=True)
class ResearchScientificObservation:
    observation_id: str
    object_id: str
    observation_time: str
    source_name: str | None = None
    source_provider: str | None = None
    source_dataset: str | None = None


def create_observation_reference(
    scientific_data: ScientificData,
) -> ResearchScientificObservation:
    if scientific_data is None:
        raise ValueError(
            "Scientific data is required"
        )

    if scientific_data.observation is None:
        raise ValueError(
            "Scientific data does not contain an observation"
        )

    object_id = scientific_data.object_id.strip().lower()

    if not object_id:
        raise ValueError(
            "Scientific data must contain an object_id"
        )

    observation_time = (
        scientific_data.observation.observation_time
    )

    if not observation_time:
        raise ValueError(
            "Scientific observation must contain an observation_time"
        )

    source = scientific_data.observation.source

    source_name = source.name if source else None
    source_provider = source.provider if source else None
    source_dataset = source.dataset if source else None

    source_identity = (
        source_name
        or source_provider
        or source_dataset
        or "unknown-source"
    )

    observation_id = (
        "scientific:"
        f"{object_id}:"
        f"{observation_time}:"
        f"{source_identity}"
    )

    return ResearchScientificObservation(
        observation_id=observation_id,
        object_id=object_id,
        observation_time=observation_time,
        source_name=source_name,
        source_provider=source_provider,
        source_dataset=source_dataset,
    )


def resolve_observation_reference(
    reference: ResearchScientificObservation,
) -> ScientificData:
    if reference is None:
        raise ValueError(
            "Scientific observation reference is required"
        )

    object_id = reference.object_id.strip().lower()

    if not object_id:
        raise ValueError(
            "Scientific observation reference must contain an object_id"
        )

    if get_celestial_object(object_id) is None:
        raise ValueError(
            f"Unknown celestial object: {object_id}"
        )

    observation_time = reference.observation_time

    if not observation_time:
        raise ValueError(
            "Scientific observation reference must contain "
            "an observation_time"
        )

    try:
        parsed_observation_time = datetime.fromisoformat(
            observation_time
        )
    except ValueError as exc:
        raise ValueError(
            "Scientific observation reference contains "
            "an invalid observation_time"
        ) from exc

    scientific_data = get_scientific_data(
        object_id,
        observation_time=parsed_observation_time,
    )

    if scientific_data is None:
        raise ValueError(
            f"No scientific data available for celestial object: "
            f"{object_id}"
        )

    return scientific_data

def _validate_observation_source_identity(
    observation_id: str,
    source_identity: str,
    scientific_data: ScientificData,
) -> None:
    if not source_identity:
        raise ValueError(
            "Scientific observation ID must contain a source identity: "
            f"{observation_id}"
        )

    observation = scientific_data.observation

    if observation is None or observation.source is None:
        raise ValueError(
            "Scientific observation does not contain a source: "
            f"{observation_id}"
        )

    actual_source_identity = (
        observation.source.name
        or observation.source.provider
        or observation.source.dataset
    )

    if actual_source_identity != source_identity:
        raise ValueError(
            "Scientific observation source mismatch: "
            f"expected {source_identity}, "
            f"resolved {actual_source_identity}"
        )

def resolve_observation_id(
    observation_id: str,
) -> ScientificData:
    if not observation_id:
        raise ValueError(
            "Scientific observation ID is required"
        )

    if not observation_id.startswith("scientific:"):
        raise ValueError(
            "Unsupported scientific observation ID: "
            f"{observation_id}"
        )

    parts = observation_id.split(":", 2)

    if len(parts) != 3:
        raise ValueError(
            "Invalid scientific observation ID: "
            f"{observation_id}"
        )

    _, object_id, observation_and_source = parts

    if ":" not in observation_and_source:
        raise ValueError(
            "Invalid scientific observation ID: "
            f"{observation_id}"
        )

    observation_time, source_identity = (
        observation_and_source.rsplit(":", 1)
    )

    if not source_identity:
        raise ValueError(
            "Scientific observation ID must contain a source identity: "
            f"{observation_id}"
        )

    reference = ResearchScientificObservation(
        observation_id=observation_id,
        object_id=object_id,
        observation_time=observation_time,
        source_name=source_identity,
    )

    scientific_data = resolve_observation_reference(
        reference
    )

    _validate_observation_source_identity(
        observation_id,
        source_identity,
        scientific_data,
    )

    return scientific_data

def resolve_observation_provenance(
    observation_id: str,
) -> ScientificProvenance:
    scientific_data = resolve_observation_id(observation_id)

    if scientific_data.provenance is None:
        raise ValueError(
            "Scientific observation does not contain provenance: "
            f"{observation_id}"
        )

    return scientific_data.provenance
