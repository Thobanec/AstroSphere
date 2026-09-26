from __future__ import annotations

from dataclasses import dataclass

import pytest

from astrosphere.monitoring.runtime import (
    MonitoringWorker,
    get_monitoring_interval_seconds,
)


@dataclass
class FakeResult:
    event: object


class FakeScheduler:
    def __init__(self):
        self.calls = 0

    def run_once(self):
        self.calls += 1

        return [
            FakeResult(event=object()),
            FakeResult(event=object()),
        ]


def test_monitoring_worker_run_once_counts_events():

    scheduler = FakeScheduler()

    worker = MonitoringWorker(
        scheduler=scheduler,
        interval_seconds=60,
    )

    result = worker.run_once()

    assert result.processed_events == 2
    assert scheduler.calls == 1


def test_monitoring_worker_stop_sets_stopped():

    scheduler = FakeScheduler()

    worker = MonitoringWorker(
        scheduler=scheduler,
        interval_seconds=60,
    )

    assert worker.stopped is False

    worker.stop()

    assert worker.stopped is True


def test_monitoring_worker_rejects_short_interval():

    scheduler = FakeScheduler()

    with pytest.raises(ValueError):

        MonitoringWorker(
            scheduler=scheduler,
            interval_seconds=59,
        )


def test_monitoring_interval_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "ASTROSPHERE_MONITORING_INTERVAL_SECONDS",
        "600",
    )

    assert (
        get_monitoring_interval_seconds()
        == 600
    )


def test_monitoring_interval_rejects_invalid_value(
    monkeypatch,
):

    monkeypatch.setenv(
        "ASTROSPHERE_MONITORING_INTERVAL_SECONDS",
        "invalid",
    )

    with pytest.raises(ValueError):

        get_monitoring_interval_seconds()


def test_monitoring_interval_rejects_short_value(
    monkeypatch,
):

    monkeypatch.setenv(
        "ASTROSPHERE_MONITORING_INTERVAL_SECONDS",
        "30",
    )

    with pytest.raises(ValueError):

        get_monitoring_interval_seconds()