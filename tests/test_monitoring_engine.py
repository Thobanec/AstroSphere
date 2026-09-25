from datetime import datetime, timezone

from astrosphere.monitoring.analyzers.asteroid_risk import (
    assess_asteroid_event,
)
from astrosphere.monitoring.analyzers.space_weather import (
    assess_space_weather_event,
)
from astrosphere.monitoring.engine import MonitoringEngine
from astrosphere.monitoring.models import MonitoringEvent
from astrosphere.monitoring.store import MonitoringStore


def _asteroid_event() -> MonitoringEvent:
    return MonitoringEvent(
        event_id="cneos-engine-event",
        event_type="asteroid_close_approach",
        source="NASA/JPL CNEOS",
        detected_at=datetime(2026, 9, 25, tzinfo=timezone.utc),
        object_id="asteroid:99942",
        object_name="99942 Apophis",
        affected_body="Earth",
        severity="information",
        status="active",
        summary="Apophis close approach.",
        data={
            "designation": "99942",
            "fullname": "99942 Apophis",
            "close_approach_time": "2026-Sep-29 10:33",
            "distance_au": 0.05,
            "distance_min_au": 0.049,
            "distance_max_au": 0.051,
            "relative_velocity_km_s": 30.0,
        },
        fingerprint="engine-asteroid-event",
    )


def _space_weather_event() -> MonitoringEvent:
    return MonitoringEvent(
        event_id="noaa-engine-event",
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
        summary="NOAA space-weather observation.",
        data={
            "observation_time": "2026-09-25T14:30:00+00:00",
            "kp": 7.0,
            "solar_wind_speed_km_s": 650.0,
            "solar_wind_density_cm3": 18.0,
            "solar_wind_temperature_k": 100000.0,
            "bt_nt": 12.0,
            "bz_nt": -12.5,
        },
        fingerprint="engine-space-weather-event",
    )


def test_engine_processes_asteroid_event(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    result = engine.process_event(_asteroid_event())

    assert result.event.event_id == "cneos-engine-event"
    assert result.event.severity == "watch"
    assert result.assessment.proximity_level == "watch"

    stored = store.get_event("cneos-engine-event")

    assert stored is not None
    assert stored.severity == "watch"


def test_engine_processes_space_weather_event(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    result = engine.process_event(_space_weather_event())

    assert result.event.event_id == "noaa-engine-event"
    assert result.event.severity == "warning"
    assert result.assessment.severity == "warning"

    stored = store.get_event("noaa-engine-event")

    assert stored is not None
    assert stored.severity == "warning"


def test_engine_deduplicates_existing_event(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    first = engine.process_event(_asteroid_event())
    second = engine.process_event(_asteroid_event())

    assert first.event.event_id == second.event.event_id

    events = store.list_events()

    assert len(events) == 1


def test_engine_creates_alert_for_warning_or_higher(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    result = engine.process_event(_space_weather_event())

    assert result.alert is not None
    assert result.alert.event_id == result.event.event_id
    assert result.alert.severity == "warning"

    alerts = store.list_alerts()

    assert len(alerts) == 1


def test_engine_does_not_alert_on_information(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    result = engine.process_event(
        _asteroid_event()
    )

    assert result.alert is None
    assert store.list_alerts() == []


def test_engine_records_source_health(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    engine.record_source_success(
        source="NASA/JPL CNEOS",
        data_time=datetime(
            2026,
            9,
            25,
            14,
            30,
            tzinfo=timezone.utc,
        ),
    )

    status = store.get_source_status(
        "NASA/JPL CNEOS"
    )

    assert status is not None
    assert status.healthy is True
    assert status.last_data_at == datetime(
        2026,
        9,
        25,
        14,
        30,
        tzinfo=timezone.utc,
    )


def test_engine_records_source_failure(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    engine.record_source_failure(
        source="NOAA SWPC",
        error="Connection timeout",
    )

    status = store.get_source_status(
        "NOAA SWPC"
    )

    assert status is not None
    assert status.healthy is False
    assert status.error == "Connection timeout"
