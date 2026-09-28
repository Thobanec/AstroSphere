from __future__ import annotations

from dataclasses import dataclass

from ..models import MonitoringEvent


@dataclass(frozen=True)
class SpaceWeatherAssessment:
    event_id: str
    affected_body: str
    severity: str
    kp: float | None
    solar_wind_speed_km_s: float | None
    solar_wind_density_cm3: float | None
    solar_wind_temperature_k: float | None
    bt_nt: float | None
    bz_nt: float | None
    observation_time: str | None
    source: str
    assessment_basis: str


def _severity_from_kp(kp: float | None) -> str:
    if kp is None:
        return "information"

    if kp >= 9:
        return "critical"

    if kp >= 7:
        return "warning"

    if kp >= 5:
        return "advisory"

    if kp >= 4:
        return "watch"

    return "information"


def assess_space_weather_event(
    event: MonitoringEvent,
) -> SpaceWeatherAssessment:
    if event.event_type != "space_weather":
        raise ValueError(
            "Space weather assessment requires a space weather event."
        )

    data = event.data

    kp_value = data.get("kp")
    wind_speed = data.get("solar_wind_speed_km_s")
    wind_density = data.get("solar_wind_density_cm3")
    wind_temperature = data.get("solar_wind_temperature_k")
    bt = data.get("bt_nt")
    bz = data.get("bz_nt")

    kp = float(kp_value) if kp_value is not None else None
    wind_speed = (
        float(wind_speed)
        if wind_speed is not None
        else None
    )
    wind_density = (
        float(wind_density)
        if wind_density is not None
        else None
    )
    wind_temperature = (
        float(wind_temperature)
        if wind_temperature is not None
        else None
    )
    bt = float(bt) if bt is not None else None
    bz = float(bz) if bz is not None else None

    if kp is not None and kp < 0:
        raise ValueError("Kp cannot be negative.")

    severity = _severity_from_kp(kp)

    return SpaceWeatherAssessment(
        event_id=event.event_id,
        affected_body=event.affected_body or "Earth",
        severity=severity,
        kp=kp,
        solar_wind_speed_km_s=wind_speed,
        solar_wind_density_cm3=wind_density,
        solar_wind_temperature_k=wind_temperature,
        bt_nt=bt,
        bz_nt=bz,
        observation_time=data.get("observation_time"),
        source=event.source,
        assessment_basis=(
            "NOAA SWPC geomagnetic Kp classification. "
            "Solar-wind and magnetic-field measurements are "
            "preserved as supporting observations."
        ),
    )
