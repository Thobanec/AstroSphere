from __future__ import annotations

from .config import get_monitoring_database_path
from .store import MonitoringStore


def get_monitoring_store() -> MonitoringStore:
    """Return the application's persistent monitoring store."""

    return MonitoringStore(
        get_monitoring_database_path()
    )


def get_monitoring_status() -> dict:
    """Return persisted monitoring source health."""

    store = get_monitoring_store()
    source_statuses = store.list_source_statuses()

    sources = [
        {
            "source": status.source,
            "healthy": status.healthy,
            "checked_at": status.checked_at.isoformat(),
            "last_success_at": (
                status.last_success_at.isoformat()
                if status.last_success_at
                else None
            ),
            "last_data_at": (
                status.last_data_at.isoformat()
                if status.last_data_at
                else None
            ),
            "error": status.error,
        }
        for status in source_statuses
    ]

    healthy = bool(sources) and all(
        source["healthy"]
        for source in sources
    )

    return {
        "enabled": True,
        "healthy": healthy,
        "sources": sources,
    }


def get_monitoring_worker_status(
    *,
    worker_id: str = "primary",
) -> dict | None:
    """Return persisted monitoring worker health."""

    store = get_monitoring_store()
    status = store.get_worker_status(worker_id)

    if status is None:
        return None

    return {
        "worker_id": status.worker_id,
        "status": status.status,
        "started_at": (
            status.started_at.isoformat()
            if status.started_at
            else None
        ),
        "last_cycle_at": (
            status.last_cycle_at.isoformat()
            if status.last_cycle_at
            else None
        ),
        "last_success_at": (
            status.last_success_at.isoformat()
            if status.last_success_at
            else None
        ),
        "last_failure_at": (
            status.last_failure_at.isoformat()
            if status.last_failure_at
            else None
        ),
        "last_cycle_duration_seconds": (
            status.last_cycle_duration_seconds
        ),
        "next_cycle_at": (
            status.next_cycle_at.isoformat()
            if status.next_cycle_at
            else None
        ),
        "interval_seconds": status.interval_seconds,
        "last_processed_events": (
            status.last_processed_events
        ),
        "last_error": status.last_error,
    }


def list_monitoring_events(
    *,
    limit: int = 100,
    event_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    source: str | None = None,
) -> list[dict]:
    """Return persisted monitoring events."""

    store = get_monitoring_store()

    events = store.list_events(
        limit=limit,
        event_type=event_type,
        severity=severity,
        status=status,
        source=source,
    )

    return [
        {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "source": event.source,
            "detected_at": event.detected_at.isoformat(),
            "event_time": (
                event.event_time.isoformat()
                if event.event_time
                else None
            ),
            "object_id": event.object_id,
            "object_name": event.object_name,
            "affected_body": event.affected_body,
            "severity": event.severity,
            "status": event.status,
            "summary": event.summary,
            "source_url": event.source_url,
            "data": event.data,
            "fingerprint": event.fingerprint,
        }
        for event in events
    ]


def list_monitoring_alerts(
    *,
    limit: int = 100,
    acknowledged: bool | None = None,
) -> list[dict]:
    """Return persisted monitoring alerts."""

    store = get_monitoring_store()

    alerts = store.list_alerts(
        limit=limit,
        acknowledged=acknowledged,
    )

    return [
        {
            "alert_id": alert.alert_id,
            "event_id": alert.event_id,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "created_at": alert.created_at.isoformat(),
            "acknowledged": alert.acknowledged,
            "metadata": alert.metadata,
        }
        for alert in alerts
    ]


def acknowledge_monitoring_alert(
    alert_id: str,
) -> bool:
    """Acknowledge a persisted monitoring alert."""

    store = get_monitoring_store()

    return store.acknowledge_alert(alert_id)
