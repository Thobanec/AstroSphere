from datetime import datetime, timezone
from pathlib import Path

from astrosphere.monitoring.analyzers.asteroid_risk import (
    assess_asteroid_event,
)
from astrosphere.monitoring.analyzers.space_weather import (
    assess_space_weather_event,
)
from astrosphere.monitoring.engine import MonitoringEngine
from astrosphere.monitoring.models import MonitoringEvent
from astrosphere.monitoring.scheduler import (
    MonitoringScheduler,
    build_monitoring_scheduler,
)
from astrosphere.monitoring.store import MonitoringStore


def test_build_monitoring_scheduler_uses_production_sources(monkeypatch):
    cneos_calls = []
    noaa_calls = []

    def fake_cneos(*, lookahead_days):
        cneos_calls.append(lookahead_days)
        return lambda: ["cneos-event"]

    def fake_noaa():
        noaa_calls.append(True)
        return lambda: "noaa-event"

    monkeypatch.setattr(
        "astrosphere.monitoring.scheduler.build_cneos_monitoring_source",
        fake_cneos,
    )
    monkeypatch.setattr(
        "astrosphere.monitoring.scheduler.build_noaa_monitoring_source",
        fake_noaa,
    )

    engine = object()

    scheduler = build_monitoring_scheduler(
        engine=engine,
        cneos_lookahead_days=45,
    )

    assert isinstance(scheduler, MonitoringScheduler)
    assert scheduler.engine is engine
    assert cneos_calls == [45]
    assert noaa_calls == [True]
    assert scheduler.cneos_source() == ["cneos-event"]
    assert scheduler.noaa_source() == "noaa-event"


def test_production_scheduler_processes_both_sources(tmp_path):
    store = MonitoringStore(
        Path(tmp_path) / "monitoring.db"
    )

    engine = MonitoringEngine(
        store=store,
        asteroid_analyzer=assess_asteroid_event,
        space_weather_analyzer=assess_space_weather_event,
    )

    detected_at = datetime(
        2026,
        9,
        25,
        12,
        0,
        tzinfo=timezone.utc,
    )

    cneos_event = MonitoringEvent(
        event_id="integration-cneos-001",
        event_type="asteroid_close_approach",
        source="NASA/JPL CNEOS",
        detected_at=detected_at,
        object_id="asteroid:99942",
        object_name="99942 Apophis",
        affected_body="Earth",
        summary="Integration CNEOS event",
        data={
            "distance_au": 0.05,
            "relative_velocity_km_s": 10.0,
        },
        fingerprint="integration-cneos-fingerprint",
    )

    noaa_event = MonitoringEvent(
        event_id="integration-noaa-001",
        event_type="space_weather",
        source="NOAA SWPC",
        detected_at=detected_at,
        affected_body="Earth",
        summary="Integration NOAA event",
        data={
            "observation_time": detected_at.isoformat(),
            "kp": 3.0,
            "solar_wind_speed_km_s": 400.0,
            "solar_wind_density_cm3": 5.0,
            "solar_wind_temperature_k": 100000.0,
            "bt_nt": 5.0,
            "bz_nt": 1.0,
        },
        fingerprint="integration-noaa-fingerprint",
    )

    scheduler = MonitoringScheduler(
        engine=engine,
        cneos_source=lambda: [cneos_event],
        noaa_source=lambda: noaa_event,
    )

    results = scheduler.run_once()

    assert len(results) == 2
    assert {result.event.event_id for result in results} == {
        "integration-cneos-001",
        "integration-noaa-001",
    }

    stored_events = store.list_events(limit=10)

    assert {event.event_id for event in stored_events} == {
        "integration-cneos-001",
        "integration-noaa-001",
    }

    cneos_status = store.get_source_status("cneos")
    noaa_status = store.get_source_status("noaa")

    assert cneos_status is not None
    assert cneos_status.healthy is True

    assert noaa_status is not None
    assert noaa_status.healthy is True
