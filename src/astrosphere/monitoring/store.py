from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    MonitoringAlert,
    MonitoringEvent,
    MonitoringSourceStatus,
    MonitoringWorkerStatus,
)


class MonitoringStore:
    """
    Persistent SQLite store for AstroSphere monitoring events,
    alerts, and source health information.
    """

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
        )
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS monitoring_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    event_time TEXT,
                    object_id TEXT,
                    object_name TEXT,
                    affected_body TEXT,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    source_url TEXT,
                    data_json TEXT NOT NULL,
                    fingerprint TEXT NOT NULL UNIQUE
                );

                CREATE INDEX IF NOT EXISTS
                    idx_monitoring_events_event_time
                    ON monitoring_events(event_time);

                CREATE INDEX IF NOT EXISTS
                    idx_monitoring_events_event_type
                    ON monitoring_events(event_type);

                CREATE INDEX IF NOT EXISTS
                    idx_monitoring_events_severity
                    ON monitoring_events(severity);

                CREATE INDEX IF NOT EXISTS
                    idx_monitoring_events_status
                    ON monitoring_events(status);

                CREATE TABLE IF NOT EXISTS monitoring_alerts (
                    alert_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    acknowledged INTEGER NOT NULL DEFAULT 0,
                    metadata_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS
                    idx_monitoring_alerts_event_id
                    ON monitoring_alerts(event_id);

                CREATE INDEX IF NOT EXISTS
                    idx_monitoring_alerts_acknowledged
                    ON monitoring_alerts(acknowledged);

                CREATE TABLE IF NOT EXISTS monitoring_sources (
                    source TEXT PRIMARY KEY,
                    healthy INTEGER NOT NULL,
                    checked_at TEXT NOT NULL,
                    last_success_at TEXT,
                    last_data_at TEXT,
                    error TEXT
                );

                CREATE TABLE IF NOT EXISTS monitoring_worker (
                    worker_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    started_at TEXT,
                    last_cycle_at TEXT,
                    last_success_at TEXT,
                    last_failure_at TEXT,
                    last_cycle_duration_seconds REAL,
                    next_cycle_at TEXT,
                    interval_seconds INTEGER,
                    last_processed_events INTEGER,
                    last_error TEXT
                );
                """
            )

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None

        if value.tzinfo is None:
            raise ValueError(
                "Stored datetimes must be timezone-aware."
            )

        return value.astimezone(timezone.utc).isoformat()

    @staticmethod
    def _deserialize_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None

        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed

    def save_event(self, event: MonitoringEvent) -> bool:
        """
        Save an event.

        Returns True when a new event was inserted.
        Returns False when the fingerprint already exists.
        """
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO monitoring_events (
                    event_id,
                    event_type,
                    source,
                    detected_at,
                    event_time,
                    object_id,
                    object_name,
                    affected_body,
                    severity,
                    status,
                    summary,
                    source_url,
                    data_json,
                    fingerprint
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.source,
                    self._serialize_datetime(event.detected_at),
                    self._serialize_datetime(event.event_time),
                    event.object_id,
                    event.object_name,
                    event.affected_body,
                    event.severity,
                    event.status,
                    event.summary,
                    event.source_url,
                    json.dumps(
                        event.data,
                        sort_keys=True,
                        default=str,
                    ),
                    event.fingerprint,
                ),
            )

            return cursor.rowcount == 1

    def get_event(self, event_id: str) -> MonitoringEvent | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM monitoring_events
                WHERE event_id = ?
                """,
                (event_id,),
            ).fetchone()

        if row is None:
            return None

        return self._event_from_row(row)

    def get_event_by_fingerprint(
        self,
        fingerprint: str,
    ) -> MonitoringEvent | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM monitoring_events
                WHERE fingerprint = ?
                """,
                (fingerprint,),
            ).fetchone()

        if row is None:
            return None

        return self._event_from_row(row)

    def list_events(
        self,
        *,
        limit: int = 100,
        event_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        source: str | None = None,
    ) -> list[MonitoringEvent]:
        query = """
            SELECT *
            FROM monitoring_events
        """

        conditions: list[str] = []
        parameters: list[Any] = []

        if event_type is not None:
            conditions.append("event_type = ?")
            parameters.append(event_type)

        if severity is not None:
            conditions.append("severity = ?")
            parameters.append(severity)

        if status is not None:
            conditions.append("status = ?")
            parameters.append(status)

        if source is not None:
            conditions.append("source = ?")
            parameters.append(source)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            ORDER BY
                COALESCE(event_time, detected_at) DESC
            LIMIT ?
        """

        parameters.append(max(1, limit))

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._event_from_row(row)
            for row in rows
        ]

    def save_alert(self, alert: MonitoringAlert) -> bool:
        """
        Save an alert.

        Returns True when inserted and False when the alert already exists.
        """
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO monitoring_alerts (
                    alert_id,
                    event_id,
                    severity,
                    title,
                    message,
                    created_at,
                    acknowledged,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.alert_id,
                    alert.event_id,
                    alert.severity,
                    alert.title,
                    alert.message,
                    self._serialize_datetime(alert.created_at),
                    int(alert.acknowledged),
                    json.dumps(
                        alert.metadata,
                        sort_keys=True,
                        default=str,
                    ),
                ),
            )

            return cursor.rowcount == 1

    def list_alerts(
        self,
        *,
        limit: int = 100,
        acknowledged: bool | None = None,
        event_id: str | None = None,
    ) -> list[MonitoringAlert]:
        query = """
            SELECT *
            FROM monitoring_alerts
        """

        parameters: list[Any] = []
        conditions: list[str] = []

        if acknowledged is not None:
            conditions.append("acknowledged = ?")
            parameters.append(int(acknowledged))

        if event_id is not None:
            conditions.append("event_id = ?")
            parameters.append(event_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            ORDER BY created_at DESC
            LIMIT ?
        """

        parameters.append(max(1, limit))

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._alert_from_row(row)
            for row in rows
        ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE monitoring_alerts
                SET acknowledged = 1
                WHERE alert_id = ?
                """,
                (alert_id,),
            )

            return cursor.rowcount == 1

    def save_source_status(
        self,
        status: MonitoringSourceStatus,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO monitoring_sources (
                    source,
                    healthy,
                    checked_at,
                    last_success_at,
                    last_data_at,
                    error
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(source) DO UPDATE SET
                    healthy = excluded.healthy,
                    checked_at = excluded.checked_at,
                    last_success_at = excluded.last_success_at,
                    last_data_at = excluded.last_data_at,
                    error = excluded.error
                """,
                (
                    status.source,
                    int(status.healthy),
                    self._serialize_datetime(status.checked_at),
                    self._serialize_datetime(status.last_success_at),
                    self._serialize_datetime(status.last_data_at),
                    status.error,
                ),
            )

    def get_source_status(
        self,
        source: str,
    ) -> MonitoringSourceStatus | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM monitoring_sources
                WHERE source = ?
                """,
                (source,),
            ).fetchone()

        if row is None:
            return None

        return self._source_status_from_row(row)

    def save_worker_status(
        self,
        status: MonitoringWorkerStatus,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO monitoring_worker (
                    worker_id,
                    status,
                    started_at,
                    last_cycle_at,
                    last_success_at,
                    last_failure_at,
                    last_cycle_duration_seconds,
                    next_cycle_at,
                    interval_seconds,
                    last_processed_events,
                    last_error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(worker_id) DO UPDATE SET
                    status = excluded.status,
                    started_at = excluded.started_at,
                    last_cycle_at = excluded.last_cycle_at,
                    last_success_at = excluded.last_success_at,
                    last_failure_at = excluded.last_failure_at,
                    last_cycle_duration_seconds =
                        excluded.last_cycle_duration_seconds,
                    next_cycle_at = excluded.next_cycle_at,
                    interval_seconds = excluded.interval_seconds,
                    last_processed_events =
                        excluded.last_processed_events,
                    last_error = excluded.last_error
                """,
                (
                    status.worker_id,
                    status.status,
                    self._serialize_datetime(
                        status.started_at
                    ),
                    self._serialize_datetime(
                        status.last_cycle_at
                    ),
                    self._serialize_datetime(
                        status.last_success_at
                    ),
                    self._serialize_datetime(
                        status.last_failure_at
                    ),
                    status.last_cycle_duration_seconds,
                    self._serialize_datetime(
                        status.next_cycle_at
                    ),
                    status.interval_seconds,
                    status.last_processed_events,
                    status.last_error,
                ),
            )


    def get_worker_status(
        self,
        worker_id: str = "primary",
    ) -> MonitoringWorkerStatus | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM monitoring_worker
                WHERE worker_id = ?
                """,
                (worker_id,),
            ).fetchone()

        if row is None:
            return None

        return MonitoringWorkerStatus(
            worker_id=row["worker_id"],
            status=row["status"],
            started_at=self._deserialize_datetime(
                row["started_at"]
            ),
            last_cycle_at=self._deserialize_datetime(
                row["last_cycle_at"]
            ),
            last_success_at=self._deserialize_datetime(
                row["last_success_at"]
            ),
            last_failure_at=self._deserialize_datetime(
                row["last_failure_at"]
            ),
            last_cycle_duration_seconds=(
                row["last_cycle_duration_seconds"]
            ),
            next_cycle_at=self._deserialize_datetime(
                row["next_cycle_at"]
            ),
            interval_seconds=row["interval_seconds"],
            last_processed_events=(
                row["last_processed_events"]
            ),
            last_error=row["last_error"],
        )

    def list_source_statuses(self) -> list[MonitoringSourceStatus]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM monitoring_sources
                ORDER BY source
                """
            ).fetchall()

        return [
            self._source_status_from_row(row)
            for row in rows
        ]

    @classmethod
    def _event_from_row(
        cls,
        row: sqlite3.Row,
    ) -> MonitoringEvent:
        return MonitoringEvent(
            event_id=row["event_id"],
            event_type=row["event_type"],
            source=row["source"],
            detected_at=cls._deserialize_datetime(
                row["detected_at"]
            ),
            event_time=cls._deserialize_datetime(
                row["event_time"]
            ),
            object_id=row["object_id"],
            object_name=row["object_name"],
            affected_body=row["affected_body"],
            severity=row["severity"],
            status=row["status"],
            summary=row["summary"],
            source_url=row["source_url"],
            data=json.loads(row["data_json"]),
            fingerprint=row["fingerprint"],
        )

    @classmethod
    def _alert_from_row(
        cls,
        row: sqlite3.Row,
    ) -> MonitoringAlert:
        return MonitoringAlert(
            alert_id=row["alert_id"],
            event_id=row["event_id"],
            severity=row["severity"],
            title=row["title"],
            message=row["message"],
            created_at=cls._deserialize_datetime(
                row["created_at"]
            ),
            acknowledged=bool(row["acknowledged"]),
            metadata=json.loads(row["metadata_json"]),
        )

    @classmethod
    def _source_status_from_row(
        cls,
        row: sqlite3.Row,
    ) -> MonitoringSourceStatus:
        return MonitoringSourceStatus(
            source=row["source"],
            healthy=bool(row["healthy"]),
            checked_at=cls._deserialize_datetime(
                row["checked_at"]
            ),
            last_success_at=cls._deserialize_datetime(
                row["last_success_at"]
            ),
            last_data_at=cls._deserialize_datetime(
                row["last_data_at"]
            ),
            error=row["error"],
        )
