from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from .models import (
    MonitoringAlert,
    MonitoringEvent,
    MonitoringSourceStatus,
)
from .store import MonitoringStore


_ALERT_SEVERITIES = frozenset(
    {
        "warning",
        "critical",
    }
)


@dataclass(frozen=True)
class MonitoringProcessResult:
    event: MonitoringEvent
    assessment: Any
    alert: MonitoringAlert | None = None


class MonitoringEngine:
    def __init__(
        self,
        *,
        store: MonitoringStore,
        asteroid_analyzer: Callable[[MonitoringEvent], Any],
        space_weather_analyzer: Callable[[MonitoringEvent], Any],
    ) -> None:
        self.store = store
        self.asteroid_analyzer = asteroid_analyzer
        self.space_weather_analyzer = space_weather_analyzer

    def process_event(
        self,
        event: MonitoringEvent,
    ) -> MonitoringProcessResult:
        existing = self.store.get_event_by_fingerprint(
            event.fingerprint
        )

        if existing is not None:
            assessment = self._assess(existing)

            alert = self._existing_alert(
                existing.event_id
            )

            return MonitoringProcessResult(
                event=existing,
                assessment=assessment,
                alert=alert,
            )

        assessment = self._assess(event)

        severity = getattr(
            assessment,
            "severity",
            None,
        )

        if severity is None:
            severity = getattr(
                assessment,
                "proximity_level",
                event.severity,
            )

        processed_event = self._with_severity(
            event,
            severity,
        )

        self.store.save_event(
            processed_event
        )

        alert = None

        if processed_event.severity in _ALERT_SEVERITIES:
            alert = self._create_alert(
                processed_event
            )

        return MonitoringProcessResult(
            event=processed_event,
            assessment=assessment,
            alert=alert,
        )

    def record_source_success(
        self,
        *,
        source: str,
        data_time: datetime | None = None,
        checked_at: datetime | None = None,
    ) -> MonitoringSourceStatus:
        checked_at = checked_at or datetime.now(
            timezone.utc
        )

        status = MonitoringSourceStatus(
            source=source,
            healthy=True,
            checked_at=checked_at,
            last_success_at=checked_at,
            last_data_at=data_time,
            error=None,
        )

        self.store.save_source_status(
            status
        )

        return status

    def record_source_failure(
        self,
        *,
        source: str,
        error: str,
        checked_at: datetime | None = None,
    ) -> MonitoringSourceStatus:
        checked_at = checked_at or datetime.now(
            timezone.utc
        )

        previous = self.store.get_source_status(
            source
        )

        status = MonitoringSourceStatus(
            source=source,
            healthy=False,
            checked_at=checked_at,
            last_success_at=(
                previous.last_success_at
                if previous is not None
                else None
            ),
            last_data_at=(
                previous.last_data_at
                if previous is not None
                else None
            ),
            error=error,
        )

        self.store.save_source_status(
            status
        )

        return status

    def _assess(
        self,
        event: MonitoringEvent,
    ) -> Any:
        if event.event_type == "asteroid_close_approach":
            return self.asteroid_analyzer(event)

        if event.event_type == "space_weather":
            return self.space_weather_analyzer(event)

        raise ValueError(
            f"Unsupported monitoring event type: "
            f"{event.event_type}"
        )

    @staticmethod
    def _with_severity(
        event: MonitoringEvent,
        severity: str,
    ) -> MonitoringEvent:
        return MonitoringEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            source=event.source,
            detected_at=event.detected_at,
            event_time=event.event_time,
            object_id=event.object_id,
            object_name=event.object_name,
            affected_body=event.affected_body,
            severity=severity,
            status=event.status,
            summary=event.summary,
            source_url=event.source_url,
            data=dict(event.data),
            fingerprint=event.fingerprint,
        )

    def _create_alert(
        self,
        event: MonitoringEvent,
    ) -> MonitoringAlert:
        created_at = datetime.now(
            timezone.utc
        )

        alert_id = (
            f"alert-{event.event_id}"
        )

        existing = self.store.list_alerts(
            event_id=event.event_id
        )

        if existing:
            return existing[0]

        alert = MonitoringAlert(
            alert_id=alert_id,
            event_id=event.event_id,
            severity=event.severity,
            title=(
                f"{event.severity.upper()}: "
                f"{event.event_type.replace('_', ' ')}"
            ),
            message=event.summary,
            created_at=created_at,
            acknowledged=False,
            metadata={
                "source": event.source,
                "object_id": event.object_id,
                "affected_body": event.affected_body,
            },
        )

        self.store.save_alert(
            alert
        )

        return alert

    def _existing_alert(
        self,
        event_id: str,
    ) -> MonitoringAlert | None:
        alerts = self.store.list_alerts(
            event_id=event_id
        )

        if not alerts:
            return None

        return alerts[0]
