from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from astrosphere.scientific.space_weather import (
    get_space_weather_data,
)

from ..models import MonitoringEvent


class NOAA_SpaceWeatherMonitoringError(RuntimeError):
    """Raised when NOAA space-weather monitoring data is invalid or unavailable."""


def _parse_observation_time(value: Any) -> datetime:
    if not value:
        raise NOAA_SpaceWeatherMonitoringError(
            "NOAA space-weather snapshot has no observation time."
        )

    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as error:
            raise NOAA_SpaceWeatherMonitoringError(
                "NOAA space-weather snapshot has an invalid observation time."
            ) from error

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _require_mapping(
    snapshot: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    value = snapshot.get(key)

    if not isinstance(value, dict):
        raise NOAA_SpaceWeatherMonitoringError(
            f"NOAA space-weather snapshot is missing {key} data."
        )

    return value


def normalize_noaa_snapshot(
    snapshot: dict[str, Any],
    *,
    detected_at: datetime | None = None,
) -> MonitoringEvent:
    if not isinstance(snapshot, dict):
        raise NOAA_SpaceWeatherMonitoringError(
            "NOAA space-weather snapshot must be a dictionary."
        )

    observation_time = _parse_observation_time(
        snapshot.get("observation_time")
    )

    solar_wind = _require_mapping(
        snapshot,
        "solar_wind",
    )

    magnetic_field = _require_mapping(
        snapshot,
        "magnetic_field",
    )

    geomagnetic = _require_mapping(
        snapshot,
        "geomagnetic",
    )

    kp = geomagnetic.get("kp")
    wind_speed = solar_wind.get("speed_km_s")
    wind_density = solar_wind.get("density_cm3")
    wind_temperature = solar_wind.get("temperature_k")
    bt = magnetic_field.get("bt_nt")
    bz = magnetic_field.get("bz_nt")

    fingerprint_source = "|".join(
        (
            observation_time.isoformat(),
            str(kp),
            str(wind_speed),
            str(wind_density),
            str(wind_temperature),
            str(bt),
            str(bz),
        )
    )

    fingerprint = hashlib.sha256(
        fingerprint_source.encode("utf-8")
    ).hexdigest()

    return MonitoringEvent(
        event_id=f"noaa-space-weather-{fingerprint[:24]}",
        event_type="space_weather",
        source="NOAA SWPC",
        detected_at=(
            detected_at
            if detected_at is not None
            else datetime.now(timezone.utc)
        ),
        event_time=observation_time,
        affected_body="Earth",
        severity="information",
        status="active",
        summary=(
            "NOAA SWPC space-weather observation "
            f"recorded at {observation_time.isoformat()}."
        ),
        source_url="https://services.swpc.noaa.gov",
        data={
            "observation_time": observation_time.isoformat(),
            "kp": kp,
            "solar_wind_speed_km_s": wind_speed,
            "solar_wind_density_cm3": wind_density,
            "solar_wind_temperature_k": wind_temperature,
            "bt_nt": bt,
            "bz_nt": bz,
        },
        fingerprint=fingerprint,
    )


def monitor_noaa_space_weather(
    *,
    detected_at: datetime | None = None,
) -> MonitoringEvent:
    try:
        weather = get_space_weather_data()
    except Exception as error:
        raise NOAA_SpaceWeatherMonitoringError(
            "Unable to retrieve NOAA SWPC space-weather monitoring data."
        ) from error

    snapshot = {
        "observation_time": weather.observation_time,
        "solar_wind": {
            "speed_km_s": weather.solar_wind.speed_km_s,
            "density_cm3": weather.solar_wind.density_cm3,
            "temperature_k": weather.solar_wind.temperature_k,
        },
        "magnetic_field": {
            "bt_nt": weather.magnetic_field.bt_nt,
            "bz_nt": weather.magnetic_field.bz_nt,
        },
        "geomagnetic": {
            "kp": weather.geomagnetic.kp,
        },
    }

    return normalize_noaa_snapshot(
        snapshot,
        detected_at=detected_at,
    )
