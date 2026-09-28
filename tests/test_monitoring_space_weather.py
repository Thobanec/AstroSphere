from datetime import datetime, timezone

from astrosphere.monitoring.analyzers.space_weather import (
    assess_space_weather_event,
)
from astrosphere.monitoring.models import MonitoringEvent


def _event(
    *,
    kp: float = 2.0,
    wind_speed: float = 420.0,
    density: float = 5.0,
    bz: float = 1.5,
) -> MonitoringEvent:
    return MonitoringEvent(
        event_id="noaa-test-event",
        event_type="space_weather",
        source="NOAA SWPC",
        detected_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
        event_time=datetime(
            2026,
            9,
            25,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        affected_body="Earth",
        severity="information",
        status="active",
        summary="NOAA SWPC space-weather observation.",
        data={
            "kp": kp,
            "solar_wind_speed_km_s": wind_speed,
            "solar_wind_density_cm3": density,
            "solar_wind_temperature_k": 100000.0,
            "bt_nt": 6.2,
            "bz_nt": bz,
        },
        fingerprint="space-weather-test",
    )


def test_quiet_space_weather_is_information():
    assessment = assess_space_weather_event(
        _event(kp=2.0)
    )

    assert assessment.severity == "information"


def test_unsettled_geomagnetic_activity_is_watch():
    assessment = assess_space_weather_event(
        _event(kp=4.0)
    )

    assert assessment.severity == "watch"


def test_storm_level_geomagnetic_activity_is_advisory():
    assessment = assess_space_weather_event(
        _event(kp=5.0)
    )

    assert assessment.severity == "advisory"


def test_strong_geomagnetic_activity_is_warning():
    assessment = assess_space_weather_event(
        _event(kp=7.0)
    )

    assert assessment.severity == "warning"


def test_extreme_geomagnetic_activity_is_critical():
    assessment = assess_space_weather_event(
        _event(kp=9.0)
    )

    assert assessment.severity == "critical"


def test_assessment_preserves_noaa_measurements():
    assessment = assess_space_weather_event(
        _event(
            kp=6.0,
            wind_speed=650.0,
            density=18.0,
            bz=-12.5,
        )
    )

    assert assessment.kp == 6.0
    assert assessment.solar_wind_speed_km_s == 650.0
    assert assessment.solar_wind_density_cm3 == 18.0
    assert assessment.bz_nt == -12.5
    assert assessment.affected_body == "Earth"


def test_non_space_weather_event_is_rejected():
    event = MonitoringEvent(
        event_id="asteroid-test-event",
        event_type="asteroid_close_approach",
        source="NASA/JPL CNEOS",
        detected_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
        affected_body="Earth",
        summary="Asteroid close approach.",
        fingerprint="asteroid-test",
    )

    try:
        assess_space_weather_event(event)
    except ValueError as error:
        assert "space weather" in str(error).lower()
    else:
        raise AssertionError(
            "Expected ValueError for non-space-weather event"
        )
