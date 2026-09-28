from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from astrosphere.monitoring.runtime import (
    MonitoringWorker,
    get_monitoring_interval_seconds,
)
from astrosphere.monitoring.store import MonitoringStore


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


class FailingScheduler:
    def run_once(self):
        raise RuntimeError("simulated monitoring failure")


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


def test_monitoring_worker_persists_successful_cycle():

    scheduler = FakeScheduler()

    with TemporaryDirectory() as temp_dir:

        database = Path(temp_dir) / "worker-health.db"
        store = MonitoringStore(database)

        worker = MonitoringWorker(
            scheduler=scheduler,
            interval_seconds=60,
            store=store,
            worker_id="test-worker",
        )

        result = worker.run_once()

        assert result.processed_events == 2

        status = store.get_worker_status("test-worker")

        assert status is not None
        assert status.worker_id == "test-worker"
        assert status.status == "running"
        assert status.last_cycle_at is not None
        assert status.last_success_at is not None
        assert status.last_failure_at is None
        assert status.last_cycle_duration_seconds is not None
        assert status.last_cycle_duration_seconds >= 0
        assert status.last_processed_events == 2
        assert status.next_cycle_at is not None
        assert status.last_error is None


def test_monitoring_worker_persists_failure():

    scheduler = FailingScheduler()

    with TemporaryDirectory() as temp_dir:

        database = Path(temp_dir) / "worker-health.db"
        store = MonitoringStore(database)

        worker = MonitoringWorker(
            scheduler=scheduler,
            interval_seconds=60,
            store=store,
            worker_id="test-worker",
        )

        with pytest.raises(RuntimeError, match="simulated monitoring failure"):
            worker.run_once()

        status = store.get_worker_status("test-worker")

        assert status is not None
        assert status.worker_id == "test-worker"
        assert status.status == "running"
        assert status.last_cycle_at is not None
        assert status.last_success_at is None
        assert status.last_failure_at is not None
        assert status.last_cycle_duration_seconds is not None
        assert status.last_cycle_duration_seconds >= 0
        assert status.next_cycle_at is not None
        assert status.last_error == "simulated monitoring failure"


def test_monitoring_worker_persists_stopped_state():

    scheduler = FakeScheduler()

    with TemporaryDirectory() as temp_dir:

        database = Path(temp_dir) / "worker-health.db"
        store = MonitoringStore(database)

        worker = MonitoringWorker(
            scheduler=scheduler,
            interval_seconds=60,
            store=store,
            worker_id="test-worker",
        )

        worker.stop()

        status = store.get_worker_status("test-worker")

        assert status is not None
        assert status.worker_id == "test-worker"
        assert status.status == "stopped"
        assert status.next_cycle_at is None
        assert status.interval_seconds == 60
