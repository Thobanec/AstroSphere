from datetime import datetime, timezone

from astrosphere.monitoring.engine import MonitoringEngine
from astrosphere.monitoring.models import MonitoringEvent
from astrosphere.monitoring.scheduler import MonitoringScheduler
from astrosphere.monitoring.store import MonitoringStore


def _asteroid_event():
    return MonitoringEvent(
        event_id="scheduler-asteroid-001",
        event_type="asteroid_close_approach",
        source="NASA/JPL CNEOS",
        detected_at=datetime.now(timezone.utc),
        object_id="asteroid:99942",
        object_name="99942 Apophis",
        affected_body="Earth",
        severity="information",
        summary="Apophis close approach.",
        data={
            "distance_au": 0.05,
            "distance_min_au": 0.049,
            "distance_max_au": 0.051,
            "relative_velocity_km_s": 5.0,
            "close_approach_time": "2026-Jan-01 00:00",
        },
        fingerprint="scheduler-asteroid-fingerprint",
    )


def _space_weather_event():
    return MonitoringEvent(
        event_id="scheduler-space-weather-001",
        event_type="space_weather",
        source="NOAA SWPC",
        detected_at=datetime.now(timezone.utc),
        event_time=datetime.now(timezone.utc),
        affected_body="Earth",
        severity="information",
        summary="NOAA space-weather observation.",
        data={
            "observation_time": datetime.now(timezone.utc).isoformat(),
            "kp": 2.0,
            "solar_wind_speed_km_s": 450.0,
            "solar_wind_density_cm3": 5.0,
            "solar_wind_temperature_k": 100000.0,
            "bt_nt": 5.0,
            "bz_nt": -2.0,
        },
        fingerprint="scheduler-space-weather-fingerprint",
    )


def _engine(store):
    from astrosphere.monitoring.analyzers.asteroid_risk import (
        assess_asteroid_event,
    )
    from astrosphere.monitoring.analyzers.space_weather import (
        assess_space_weather_event,
    )

    return MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )


def test_scheduler_run_once_processes_cneos_and_noaa(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    engine = _engine(store)

    scheduler = MonitoringScheduler(
        engine=engine,
        cneos_source=lambda: [_asteroid_event()],
        noaa_source=lambda: _space_weather_event(),
    )

    results = scheduler.run_once()

    assert len(results) == 2
    assert {
        result.event.event_type
        for result in results
    } == {
        "asteroid_close_approach",
        "space_weather",
    }

    events = store.list_events(limit=10)

    assert len(events) == 2


def test_scheduler_records_successful_source_health(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    engine = _engine(store)

    scheduler = MonitoringScheduler(
        engine=engine,
        cneos_source=lambda: [_asteroid_event()],
        noaa_source=lambda: _space_weather_event(),
    )

    scheduler.run_once()

    cneos_status = store.get_source_status("cneos")
    noaa_status = store.get_source_status("noaa")

    assert cneos_status is not None
    assert cneos_status.healthy is True

    assert noaa_status is not None
    assert noaa_status.healthy is True


def test_scheduler_records_cneos_failure(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    engine = _engine(store)

    def failing_cneos():
        raise RuntimeError("CNEOS unavailable")

    scheduler = MonitoringScheduler(
        engine=engine,
        cneos_source=failing_cneos,
        noaa_source=lambda: _space_weather_event(),
    )

    results = scheduler.run_once()

    assert len(results) == 1
    assert results[0].event.event_type == "space_weather"

    status = store.get_source_status("cneos")

    assert status is not None
    assert status.healthy is False
    assert status.error == "CNEOS unavailable"


def test_scheduler_records_noaa_failure(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    engine = _engine(store)

    def failing_noaa():
        raise RuntimeError("NOAA unavailable")

    scheduler = MonitoringScheduler(
        engine=engine,
        cneos_source=lambda: [_asteroid_event()],
        noaa_source=failing_noaa,
    )

    results = scheduler.run_once()

    assert len(results) == 1
    assert results[0].event.event_type == "asteroid_close_approach"

    status = store.get_source_status("noaa")

    assert status is not None
    assert status.healthy is False
    assert status.error == "NOAA unavailable"


def test_scheduler_does_not_stop_when_one_source_fails(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    engine = _engine(store)

    scheduler = MonitoringScheduler(
        engine=engine,
        cneos_source=lambda: [_asteroid_event()],
        noaa_source=lambda: (_ for _ in ()).throw(
            RuntimeError("NOAA unavailable")
        ),
    )

    results = scheduler.run_once()

    assert len(results) == 1
    assert results[0].event.event_type == "asteroid_close_approach"
