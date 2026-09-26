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