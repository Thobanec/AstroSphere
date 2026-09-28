from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .engine import MonitoringEngine, MonitoringProcessResult
from .sources.production import (
    build_cneos_monitoring_source,
    build_noaa_monitoring_source,
)


@dataclass(frozen=True)
class MonitoringSourceRun:
    source: str
    results: tuple[MonitoringProcessResult, ...]
    healthy: bool
    error: str | None = None


class MonitoringScheduler:
    """Coordinates one monitoring cycle across configured sources."""

    def __init__(
        self,
        *,
        engine: MonitoringEngine,
        cneos_source: Callable[[], Iterable[Any]],
        noaa_source: Callable[[], Any],
    ) -> None:
        self.engine = engine
        self.cneos_source = cneos_source
        self.noaa_source = noaa_source

    def run_once(self) -> list[MonitoringProcessResult]:
        """Run one complete monitoring cycle.

        Each source is isolated so that failure of one source does not
        prevent the remaining sources from being processed.
        """
        results: list[MonitoringProcessResult] = []

        cneos_run = self._run_cneos()
        results.extend(cneos_run.results)

        noaa_run = self._run_noaa()
        results.extend(noaa_run.results)

        return results

    def _run_cneos(self) -> MonitoringSourceRun:
        checked_at = datetime.now(timezone.utc)

        try:
            events = list(self.cneos_source())

            processed: list[MonitoringProcessResult] = []

            for event in events:
                processed.append(
                    self.engine.process_event(event)
                )

            data_time = max(
                (
                    result.event.event_time
                    or result.event.detected_at
                    for result in processed
                ),
                default=None,
            )

            self.engine.record_source_success(
                source="cneos",
                checked_at=checked_at,
                data_time=data_time,
            )

            return MonitoringSourceRun(
                source="cneos",
                results=tuple(processed),
                healthy=True,
            )

        except Exception as error:
            self.engine.record_source_failure(
                source="cneos",
                error=str(error),
                checked_at=checked_at,
            )

            return MonitoringSourceRun(
                source="cneos",
                results=(),
                healthy=False,
                error=str(error),
            )

    def _run_noaa(self) -> MonitoringSourceRun:
        checked_at = datetime.now(timezone.utc)

        try:
            event = self.noaa_source()

            result = self.engine.process_event(event)

            data_time = (
                result.event.event_time
                or result.event.detected_at
            )

            self.engine.record_source_success(
                source="noaa",
                checked_at=checked_at,
                data_time=data_time,
            )

            return MonitoringSourceRun(
                source="noaa",
                results=(result,),
                healthy=True,
            )

        except Exception as error:
            self.engine.record_source_failure(
                source="noaa",
                error=str(error),
                checked_at=checked_at,
            )

            return MonitoringSourceRun(
                source="noaa",
                results=(),
                healthy=False,
                error=str(error),
            )


def build_monitoring_scheduler(
    *,
    engine: MonitoringEngine,
    cneos_lookahead_days: int = 30,
) -> MonitoringScheduler:
    """Build a scheduler using AstroSphere's real monitoring sources."""

    return MonitoringScheduler(
        engine=engine,
        cneos_source=build_cneos_monitoring_source(
            lookahead_days=cneos_lookahead_days,
        ),
        noaa_source=build_noaa_monitoring_source(),
    )
