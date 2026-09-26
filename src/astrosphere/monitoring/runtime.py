from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass
from typing import Callable

from .scheduler import MonitoringScheduler


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

        self._stop_event = threading.Event()

    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def stop(self) -> None:
        LOGGER.info(
            "AstroSphere monitoring worker stopping."
        )

        self._stop_event.set()

    def run_once(self) -> MonitoringWorkerRun:
        LOGGER.info(
            "Starting AstroSphere monitoring cycle."
        )

        results = self.scheduler.run_once()

        LOGGER.info(
            "Monitoring cycle complete: %d processed events.",
            len(results),
        )

        return MonitoringWorkerRun(
            processed_events=len(results),
        )

    def run_forever(
        self,
        *,
        on_cycle: Callable[
            [MonitoringWorkerRun],
            None,
        ]
        | None = None,
    ) -> None:
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
                    "AstroSphere monitoring cycle failed."
                )

            if self.stopped:
                break

            LOGGER.info(
                "Next monitoring cycle in %d seconds.",
                self.interval_seconds,
            )

            self._stop_event.wait(
                self.interval_seconds
            )

        LOGGER.info(
            "AstroSphere monitoring worker stopped."
        )