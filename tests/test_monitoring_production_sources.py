from datetime import datetime, timezone

from astrosphere.monitoring.sources import production


def test_build_cneos_monitoring_source_uses_rolling_window(monkeypatch):
    captured = {}

    fixed_now = datetime(
        2026,
        9,
        25,
        10,
        30,
        tzinfo=timezone.utc,
    )

    class FixedDateTime:
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(
        production,
        "datetime",
        FixedDateTime,
    )

    def fake_monitor(
        *,
        date_min,
        date_max,
        detected_at,
    ):
        captured["date_min"] = date_min
        captured["date_max"] = date_max
        captured["detected_at"] = detected_at
        return ["event"]

    monkeypatch.setattr(
        production,
        "monitor_cneos_close_approaches",
        fake_monitor,
    )

    source = production.build_cneos_monitoring_source(
        lookahead_days=30,
    )

    assert source() == ["event"]
    assert captured["date_min"] == "2026-09-25"
    assert captured["date_max"] == "2026-10-25"
    assert captured["detected_at"] == fixed_now


def test_build_cneos_monitoring_source_rejects_negative_window():
    try:
        production.build_cneos_monitoring_source(
            lookahead_days=-1,
        )
    except ValueError as error:
        assert str(error) == "lookahead_days must be >= 0."
    else:
        raise AssertionError("Expected ValueError")


def test_build_noaa_monitoring_source_passes_detection_time(monkeypatch):
    captured = {}

    fixed_now = datetime(
        2026,
        9,
        25,
        10,
        45,
        tzinfo=timezone.utc,
    )

    class FixedDateTime:
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(
        production,
        "datetime",
        FixedDateTime,
    )

    def fake_monitor(*, detected_at):
        captured["detected_at"] = detected_at
        return "event"

    monkeypatch.setattr(
        production,
        "monitor_noaa_space_weather",
        fake_monitor,
    )

    source = production.build_noaa_monitoring_source()

    assert source() == "event"
    assert captured["detected_at"] == fixed_now
