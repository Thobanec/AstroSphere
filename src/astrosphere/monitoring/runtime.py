from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from .models import MonitoringWorkerStatus
from .scheduler import MonitoringScheduler
from .store import MonitoringStore

LOGGER = logging.getLogger(__name__)

DEFAULT_MONITORING_INTERVAL_SECONDS = 900


def get_monitoring_interval_seconds() -> int:
    value = os.getenv(
        "ASTROSPHERE_MONITORING_INTERVAL_SECONDS",
        str(DEFAULT_MONITORING_INTERVAL_SECONDS),
    )
    try:
        interval = int(value)
    except ValueError as exc:
        raise ValueError(
            "ASTROSPHERE_MONITORING_INTERVAL_SECONDS "
            "must be an integer."
        ) from exc
    if interval < 60:
        raise ValueError(
            "ASTROSPHERE_MONITORING_INTERVAL_SECONDS "
            "must be at least 60 seconds."
        )
    return interval


@dataclass(frozen=True)
class MonitoringWorkerRun:
    processed_events: int


class MonitoringWorker:
    """
    Long-running process coordinator for AstroSphere monitoring.

    The worker executes one monitoring cycle immediately and then
    waits for the configured interval before executing the next cycle.
    """

    def __init__(
        self,
        *,
        scheduler: MonitoringScheduler,
        interval_seconds: int | None = None,
        store: MonitoringStore | None = None,
        worker_id: str = "primary",
    ) -> None:
        self.scheduler = scheduler
        self.interval_seconds = (
            interval_seconds
            if interval_seconds is not None
            else get_monitoring_interval_seconds()
        )
        if self.interval_seconds < 60:
            raise ValueError(
                "interval_seconds must be at least 60 seconds."
            )

        self.store = store
        self.worker_id = worker_id
        self._stop_event = threading.Event()

        self._started_at: datetime | None = None
        self._last_cycle_at: datetime | None = None
        self._last_success_at: datetime | None = None
        self._last_failure_at: datetime | None = None
        self._last_cycle_duration_seconds: float | None = None
        self._next_cycle_at: datetime | None = None
        self._last_processed_events: int | None = None
        self._last_error: str | None = None

    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def _persist_status(
        self,
        *,
        status: str,
    ) -> None:
        if self.store is None:
            return

        self.store.save_worker_status(
            MonitoringWorkerStatus(
                worker_id=self.worker_id,
                status=status,
                started_at=self._started_at,
                last_cycle_at=self._last_cycle_at,
                last_success_at=self._last_success_at,
                last_failure_at=self._last_failure_at,
                last_cycle_duration_seconds=(
                    self._last_cycle_duration_seconds
                ),
                next_cycle_at=self._next_cycle_at,
                interval_seconds=self.interval_seconds,
                last_processed_events=self._last_processed_events,
                last_error=self._last_error,
            )
        )

    def stop(self) -> None:
        LOGGER.info(
            "AstroSphere monitoring worker stopping."
        )
        self._stop_event.set()
        self._next_cycle_at = None
        self._persist_status(status="stopped")

    def run_once(self) -> MonitoringWorkerRun:
        cycle_started_at = datetime.now(timezone.utc)
        cycle_started = time.perf_counter()

        self._last_cycle_at = cycle_started_at
        self._persist_status(status="running")

        LOGGER.info(
            "Starting AstroSphere monitoring cycle."
        )

        try:
            results = self.scheduler.run_once()

            duration = time.perf_counter() - cycle_started
            completed_at = datetime.now(timezone.utc)

            self._last_success_at = completed_at
            self._last_cycle_duration_seconds = duration
            self._last_processed_events = len(results)
            self._last_error = None
            self._next_cycle_at = (
                completed_at
                + timedelta(seconds=self.interval_seconds)
            )

            self._persist_status(status="running")

            LOGGER.info(
                "Monitoring cycle complete: %d processed events.",
                len(results),
            )

            return MonitoringWorkerRun(
                processed_events=len(results),
            )

        except Exception as exc:
            duration = time.perf_counter() - cycle_started
            failed_at = datetime.now(timezone.utc)

            self._last_failure_at = failed_at
            self._last_cycle_duration_seconds = duration
            self._last_error = str(exc)
            self._next_cycle_at = (
                failed_at
                + timedelta(seconds=self.interval_seconds)
            )

            self._persist_status(status="running")

            LOGGER.exception(
                "AstroSphere monitoring cycle failed."
            )

            raise

    def run_forever(
        self,
        *,
        on_cycle: Callable[[MonitoringWorkerRun], None] | None = None,
    ) -> None:
        self._started_at = datetime.now(timezone.utc)
        self._stop_event.clear()
        self._persist_status(status="running")

        LOGGER.info(
            "AstroSphere monitoring worker started. "
            "Interval: %d seconds.",
            self.interval_seconds,
        )

        while not self.stopped:
            try:
                result = self.run_once()
                if on_cycle is not None:
                    on_cycle(result)
            except Exception:
                LOGGER.exception(
                    "Monitoring worker continuing after cycle failure."
                )

            if self.stopped:
                break

            self._next_cycle_at = (
                datetime.now(timezone.utc)
                + timedelta(seconds=self.interval_seconds)
            )
            self._persist_status(status="running")

            LOGGER.info(
                "Next monitoring cycle in %d seconds.",
                self.interval_seconds,
            )

            self._stop_event.wait(self.interval_seconds)

        self._next_cycle_at = None
        self._persist_status(status="stopped")

        LOGGER.info(
            "AstroSphere monitoring worker stopped."
        )
