from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class MonitoringEvent:
    """
    Normalized scientific event observed by AstroSphere monitoring.
    """

    event_id: str
    event_type: str
    source: str

    detected_at: datetime
    event_time: datetime | None = None

    object_id: str | None = None
    object_name: str | None = None
    affected_body: str | None = None

    severity: str = "information"
    status: str = "active"

    summary: str = ""

    source_url: str | None = None

    data: dict[str, Any] = field(default_factory=dict)

    fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.detected_at.tzinfo is None:
            raise ValueError(
                "detected_at must be timezone-aware."
            )

        if self.event_time is not None and self.event_time.tzinfo is None:
            raise ValueError(
                "event_time must be timezone-aware."
            )

        if not self.fingerprint:
            object.__setattr__(
                self,
                "fingerprint",
                self.event_id,
            )


@dataclass(frozen=True)
class MonitoringAlert:
    """
    Alert generated from a monitored scientific event.
    """

    alert_id: str
    event_id: str

    severity: str
    title: str
    message: str

    created_at: datetime

    acknowledged: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )


@dataclass(frozen=True)
class MonitoringSourceStatus:
    """
    Health/status information for an external monitoring source.
    """

    source: str

    healthy: bool

    checked_at: datetime

    last_success_at: datetime | None = None

    last_data_at: datetime | None = None

    error: str | None = None

    def __post_init__(self) -> None:
        if self.checked_at.tzinfo is None:
            raise ValueError(
                "checked_at must be timezone-aware."
            )

        if (
            self.last_success_at is not None
            and self.last_success_at.tzinfo is None
        ):
            raise ValueError(
                "last_success_at must be timezone-aware."
            )

        if (
            self.last_data_at is not None
            and self.last_data_at.tzinfo is None
        ):
            raise ValueError(
                "last_data_at must be timezone-aware."
            )


def utc_now() -> datetime:
    """
    Return the current timezone-aware UTC timestamp.
    """

    return datetime.now(timezone.utc)

@dataclass(frozen=True)
class MonitoringWorkerStatus:
    worker_id: str
    status: str
    started_at: datetime | None = None
    last_cycle_at: datetime | None = None
    last_success_at: datetime | None = None
    last_failure_at: datetime | None = None
    last_cycle_duration_seconds: float | None = None
    next_cycle_at: datetime | None = None
    interval_seconds: int | None = None
    last_processed_events: int | None = None
    last_error: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "started_at",
            "last_cycle_at",
            "last_success_at",
            "last_failure_at",
            "next_cycle_at",
        ):
            value = getattr(self, field_name)
            if value is not None and value.tzinfo is None:
                raise ValueError(
                    f"{field_name} must be timezone-aware."
                )