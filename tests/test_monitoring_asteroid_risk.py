from datetime import datetime, timezone

from astrosphere.monitoring.models import MonitoringEvent
from astrosphere.monitoring.analyzers.asteroid_risk import (
    assess_asteroid_event,
)


def _event(
    *,
    distance_au: float,
    approach_time: str = "2026-09-29 08:33",
    velocity_km_s: float = 56.563,
) -> MonitoringEvent:
    return MonitoringEvent(
        event_id="cneos-test-event",
        event_type="asteroid_close_approach",
        source="NASA/JPL CNEOS",
        detected_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
        object_id="asteroid:99942",
        object_name="99942 Apophis",
        affected_body="Earth",
        severity="information",
        status="active",
        summary="99942 Apophis has a recorded Earth close approach.",
        data={
            "designation": "99942",
            "fullname": "99942 Apophis",
            "close_approach_time": approach_time,
            "distance_au": distance_au,
            "distance_min_au": distance_au * 0.99,
            "distance_max_au": distance_au * 1.01,
            "relative_velocity_km_s": velocity_km_s,
        },
        fingerprint="asteroid-risk-test",
    )


def test_distant_close_approach_is_information():
    assessment = assess_asteroid_event(_event(distance_au=0.10))

    assert assessment.proximity_level == "information"
    assert assessment.impact_risk_status == "not_assessed"
    assert "CNEOS close-approach" in assessment.assessment_basis


def test_approach_within_watch_distance_is_watch():
    assessment = assess_asteroid_event(_event(distance_au=0.05))

    assert assessment.proximity_level == "watch"


def test_very_close_approach_is_advisory():
    assessment = assess_asteroid_event(_event(distance_au=0.01))

    assert assessment.proximity_level == "advisory"


def test_extremely_close_approach_is_warning():
    assessment = assess_asteroid_event(_event(distance_au=0.005))

    assert assessment.proximity_level == "warning"


def test_very_extreme_close_approach_is_critical():
    assessment = assess_asteroid_event(_event(distance_au=0.002))

    assert assessment.proximity_level == "critical"


def test_assessment_preserves_cneos_measurements():
    assessment = assess_asteroid_event(
        _event(
            distance_au=0.0123,
            velocity_km_s=22.5,
        )
    )

    assert assessment.object_id == "asteroid:99942"
    assert assessment.object_name == "99942 Apophis"
    assert assessment.distance_au == 0.0123
    assert assessment.relative_velocity_km_s == 22.5
    assert assessment.affected_body == "Earth"


def test_non_asteroid_event_is_rejected():
    event = MonitoringEvent(
        event_id="test-space-weather",
        event_type="space_weather",
        source="NOAA SWPC",
        detected_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
        affected_body="Earth",
        summary="Space weather event",
        fingerprint="space-weather-test",
    )

    try:
        assess_asteroid_event(event)
    except ValueError as error:
        assert "asteroid" in str(error).lower()
    else:
        raise AssertionError("Expected ValueError for non-asteroid event")
