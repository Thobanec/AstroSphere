from datetime import datetime, timezone

import pytest

from astrosphere.monitoring.models import MonitoringEvent
from astrosphere.monitoring.sources.noaa import (
    NOAA_SpaceWeatherMonitoringError,
    normalize_noaa_snapshot,
)


def _snapshot(
    *,
    kp: float = 2.0,
    wind_speed: float = 420.0,
    density: float = 5.0,
    bz: float = 1.5,
):
    return {
        "observation_time": "2026-09-25T14:30:00+00:00",
        "solar_wind": {
            "speed_km_s": wind_speed,
            "density_cm3": density,
            "temperature_k": 100000.0,
        },
        "magnetic_field": {
            "bt_nt": 6.2,
            "bz_nt": bz,
        },
        "geomagnetic": {
            "kp": kp,
        },
    }


def test_normalize_noaa_snapshot_creates_space_weather_event():
    event = normalize_noaa_snapshot(
        _snapshot(),
        detected_at=datetime(2026, 9, 25, 14, 35, tzinfo=timezone.utc),
    )

    assert isinstance(event, MonitoringEvent)
    assert event.event_type == "space_weather"
    assert event.source == "NOAA SWPC"
    assert event.affected_body == "Earth"
    assert event.status == "active"
    assert event.severity == "information"


def test_normalize_noaa_snapshot_preserves_measurements():
    event = normalize_noaa_snapshot(_snapshot())

    assert event.data["kp"] == 2.0
    assert event.data["solar_wind_speed_km_s"] == 420.0
    assert event.data["solar_wind_density_cm3"] == 5.0
    assert event.data["solar_wind_temperature_k"] == 100000.0
    assert event.data["bt_nt"] == 6.2
    assert event.data["bz_nt"] == 1.5


def test_normalize_noaa_snapshot_preserves_observation_time():
    event = normalize_noaa_snapshot(_snapshot())

    assert event.event_time == datetime(
        2026,
        9,
        25,
        14,
        30,
        tzinfo=timezone.utc,
    )


def test_normalize_noaa_snapshot_creates_stable_fingerprint():
    first = normalize_noaa_snapshot(_snapshot())
    second = normalize_noaa_snapshot(_snapshot())

    assert first.fingerprint == second.fingerprint
    assert first.event_id == second.event_id


def test_normalize_noaa_snapshot_rejects_missing_observation_time():
    snapshot = _snapshot()
    snapshot.pop("observation_time")

    with pytest.raises(NOAA_SpaceWeatherMonitoringError):
        normalize_noaa_snapshot(snapshot)


def test_normalize_noaa_snapshot_rejects_missing_geomagnetic_data():
    snapshot = _snapshot()
    snapshot.pop("geomagnetic")

    with pytest.raises(NOAA_SpaceWeatherMonitoringError):
        normalize_noaa_snapshot(snapshot)
