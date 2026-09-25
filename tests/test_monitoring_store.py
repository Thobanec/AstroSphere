from datetime import datetime, timezone

from astrosphere.monitoring.models import (
    MonitoringAlert,
    MonitoringEvent,
    MonitoringSourceStatus,
)
from astrosphere.monitoring.store import MonitoringStore


def test_event_persistence_and_duplicate_detection(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    now = datetime.now(timezone.utc)

    event = MonitoringEvent(
        event_id="test-event-001",
        event_type="asteroid_close_approach",
        source="unit-test",
        detected_at=now,
        event_time=now,
        object_id="asteroid:99942",
        object_name="Apophis",
        affected_body="Earth",
        severity="watch",
        status="active",
        summary="Test asteroid close approach.",
        data={"distance_km": 300000},
        fingerprint="test-fingerprint-001",
    )

    assert store.save_event(event) is True
    assert store.save_event(event) is False

    loaded = store.get_event("test-event-001")

    assert loaded is not None
    assert loaded.event_id == event.event_id
    assert loaded.object_id == "asteroid:99942"
    assert loaded.object_name == "Apophis"
    assert loaded.data["distance_km"] == 300000


def test_event_lookup_by_fingerprint(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    now = datetime.now(timezone.utc)

    event = MonitoringEvent(
        event_id="test-event-002",
        event_type="space_weather",
        source="unit-test",
        detected_at=now,
        summary="Test space weather event.",
        fingerprint="unique-fingerprint-002",
    )

    store.save_event(event)

    loaded = store.get_event_by_fingerprint(
        "unique-fingerprint-002"
    )

    assert loaded is not None
    assert loaded.event_id == "test-event-002"


def test_event_filtering(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    now = datetime.now(timezone.utc)

    events = [
        MonitoringEvent(
            event_id="event-info",
            event_type="astronomical_event",
            source="unit-test",
            detected_at=now,
            severity="information",
            status="active",
            summary="Informational event.",
            fingerprint="fp-info",
        ),
        MonitoringEvent(
            event_id="event-watch",
            event_type="asteroid_close_approach",
            source="unit-test",
            detected_at=now,
            severity="watch",
            status="active",
            summary="Watch event.",
            fingerprint="fp-watch",
        ),
        MonitoringEvent(
            event_id="event-warning",
            event_type="space_weather",
            source="unit-test",
            detected_at=now,
            severity="warning",
            status="active",
            summary="Warning event.",
            fingerprint="fp-warning",
        ),
    ]

    for event in events:
        assert store.save_event(event) is True

    watch_events = store.list_events(
        severity="watch"
    )

    assert len(watch_events) == 1
    assert watch_events[0].event_id == "event-watch"

    asteroid_events = store.list_events(
        event_type="asteroid_close_approach"
    )

    assert len(asteroid_events) == 1
    assert asteroid_events[0].object_id is None


def test_alert_persistence_and_acknowledgement(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    now = datetime.now(timezone.utc)

    alert = MonitoringAlert(
        alert_id="alert-test-001",
        event_id="event-test-001",
        severity="warning",
        title="Test warning",
        message="Test monitoring alert.",
        created_at=now,
        metadata={"source": "unit-test"},
    )

    assert store.save_alert(alert) is True
    assert store.save_alert(alert) is False

    alerts = store.list_alerts(
        acknowledged=False
    )

    assert len(alerts) == 1
    assert alerts[0].alert_id == "alert-test-001"
    assert alerts[0].acknowledged is False

    assert store.acknowledge_alert(
        "alert-test-001"
    ) is True

    alerts = store.list_alerts(
        acknowledged=True
    )

    assert len(alerts) == 1
    assert alerts[0].acknowledged is True


def test_source_status_persistence_and_update(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    now = datetime.now(timezone.utc)

    healthy = MonitoringSourceStatus(
        source="cneos",
        healthy=True,
        checked_at=now,
        last_success_at=now,
        last_data_at=now,
    )

    store.save_source_status(healthy)

    loaded = store.get_source_status("cneos")

    assert loaded is not None
    assert loaded.source == "cneos"
    assert loaded.healthy is True

    failed = MonitoringSourceStatus(
        source="cneos",
        healthy=False,
        checked_at=now,
        last_success_at=now,
        last_data_at=now,
        error="Test source failure.",
    )

    store.save_source_status(failed)

    updated = store.get_source_status("cneos")

    assert updated is not None
    assert updated.healthy is False
    assert updated.error == "Test source failure."


def test_list_source_statuses(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    now = datetime.now(timezone.utc)

    for source in ("cneos", "noaa"):
        store.save_source_status(
            MonitoringSourceStatus(
                source=source,
                healthy=True,
                checked_at=now,
            )
        )

    statuses = store.list_source_statuses()

    assert [status.source for status in statuses] == [
        "cneos",
        "noaa",
    ]



def test_list_alerts_can_filter_by_event_id(tmp_path):
    store = MonitoringStore(tmp_path / "monitoring.db")

    now = datetime.now(timezone.utc)

    store.save_alert(
        MonitoringAlert(
            alert_id="alert-event-001",
            event_id="event-001",
            severity="warning",
            title="Warning event 001",
            message="Test warning.",
            created_at=now,
        )
    )

    store.save_alert(
        MonitoringAlert(
            alert_id="alert-event-002",
            event_id="event-002",
            severity="critical",
            title="Critical event 002",
            message="Test critical.",
            created_at=now,
        )
    )

    alerts = store.list_alerts(
        event_id="event-001"
    )

    assert len(alerts) == 1
    assert alerts[0].alert_id == "alert-event-001"
    assert alerts[0].event_id == "event-001"
