from __future__ import annotations

from dataclasses import dataclass

from ..models import MonitoringEvent


# These are proximity-monitoring thresholds, not impact-probability
# thresholds. They are intentionally kept separate from CNEOS Sentry
# impact-risk assessments.
INFORMATION_DISTANCE_AU = 0.05
ADVISORY_DISTANCE_AU = 0.01
WARNING_DISTANCE_AU = 0.005
CRITICAL_DISTANCE_AU = 0.002

AU_KM = 149_597_870.7


@dataclass(frozen=True)
class AsteroidRiskAssessment:
    event_id: str
    object_id: str
    object_name: str
    affected_body: str
    proximity_level: str
    impact_risk_status: str
    assessment_basis: str
    distance_au: float
    distance_km: float
    distance_min_au: float | None
    distance_max_au: float | None
    relative_velocity_km_s: float
    close_approach_time: str
    source: str


def _proximity_level(distance_au: float) -> str:
    if distance_au <= CRITICAL_DISTANCE_AU:
        return "critical"

    if distance_au <= WARNING_DISTANCE_AU:
        return "warning"

    if distance_au <= ADVISORY_DISTANCE_AU:
        return "advisory"

    if distance_au <= INFORMATION_DISTANCE_AU:
        return "watch"

    return "information"


def assess_asteroid_event(event: MonitoringEvent) -> AsteroidRiskAssessment:
    if event.event_type != "asteroid_close_approach":
        raise ValueError(
            "Asteroid risk assessment requires an asteroid close-approach event."
        )

    distance_au = float(event.data["distance_au"])
    distance_min_au = event.data.get("distance_min_au")
    distance_max_au = event.data.get("distance_max_au")
    relative_velocity_km_s = float(event.data["relative_velocity_km_s"])

    if distance_au < 0:
        raise ValueError("Asteroid close-approach distance cannot be negative.")

    if relative_velocity_km_s < 0:
        raise ValueError("Asteroid relative velocity cannot be negative.")

    return AsteroidRiskAssessment(
        event_id=event.event_id,
        object_id=event.object_id or "",
        object_name=event.object_name or event.data.get("fullname", "Unknown asteroid"),
        affected_body=event.affected_body or "Earth",
        proximity_level=_proximity_level(distance_au),
        impact_risk_status="not_assessed",
        assessment_basis=(
            "CNEOS close-approach proximity data; "
            "impact probability is not assessed by this analyzer."
        ),
        distance_au=distance_au,
        distance_km=distance_au * AU_KM,
        distance_min_au=(
            float(distance_min_au)
            if distance_min_au is not None
            else None
        ),
        distance_max_au=(
            float(distance_max_au)
            if distance_max_au is not None
            else None
        ),
        relative_velocity_km_s=relative_velocity_km_s,
        close_approach_time=str(
            event.data.get("close_approach_time", "")
        ),
        source=event.source,
    )
