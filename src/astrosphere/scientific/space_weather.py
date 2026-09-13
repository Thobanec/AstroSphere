import json
import threading
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

from astrosphere.models.scientific import (
    DataSource,
    Geomagnetic,
    MagneticField,
    ScientificProvenance,
    SolarWind,
    SpaceWeatherData,
)


_SWPC_BASE_URL = (
    "https://services.swpc.noaa.gov"
)

_SWPC_RTSW_WIND_URL = (
    f"{_SWPC_BASE_URL}/json/rtsw/rtsw_wind_1m.json"
)

_SWPC_RTSW_MAG_URL = (
    f"{_SWPC_BASE_URL}/json/rtsw/rtsw_mag_1m.json"
)

_SWPC_KP_URL = (
    f"{_SWPC_BASE_URL}/products/noaa-planetary-k-index.json"
)

_SWPC_SOURCE = DataSource(
    name="NOAA Space Weather Prediction Center",
    provider="NOAA SWPC",
    url=_SWPC_BASE_URL,
    dataset="Real-Time Solar Wind and Geomagnetic Data",
)

_CACHE_TTL = timedelta(minutes=5)

_CACHE = {}
_CACHE_LOCK = threading.Lock()


class SpaceWeatherServiceError(
    RuntimeError
):
    """Raised when NOAA space-weather data cannot be retrieved."""


def _fetch_json(url):
    request = Request(
        url,
        headers={
            "User-Agent": "AstroSphere/1.0"
        },
    )

    try:
        with urlopen(
            request,
            timeout=15,
        ) as response:
            return json.load(response)
    except (
        OSError,
        TimeoutError,
        json.JSONDecodeError,
    ) as exc:
        raise SpaceWeatherServiceError(
            "Unable to retrieve NOAA SWPC data."
        ) from exc


def _cache_get(key):
    now = datetime.now(timezone.utc)

    with _CACHE_LOCK:
        entry = _CACHE.get(key)

        if entry is None:
            return None

        cached_at, value = entry

        if now - cached_at < _CACHE_TTL:
            return value

        return None


def _cache_set(key, value):
    with _CACHE_LOCK:
        _CACHE[key] = (
            datetime.now(timezone.utc),
            value,
        )


def _cache_get_stale(key):
    with _CACHE_LOCK:
        entry = _CACHE.get(key)

        if entry is None:
            return None

        return entry[1]


def _to_float(value):
    if value is None:
        return None

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None


def _normalize_time(value):
    if not value:
        return None

    text = str(value).strip()

    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def _latest_object_record(
    records,
    prefer_active=False,
):
    if not isinstance(records, list):
        return None

    valid_records = []

    for record in records:
        if not isinstance(record, dict):
            continue

        timestamp = (
            record.get("time_tag")
            or record.get("time_tag_1")
            or record.get("time")
        )

        parsed_time = _normalize_time(
            timestamp
        )

        if parsed_time is None:
            continue

        valid_records.append(
            (
                parsed_time,
                record,
            )
        )

    if not valid_records:
        return None

    if prefer_active:
        active_records = [
            item
            for item in valid_records
            if item[1].get("active") is True
        ]

        if active_records:
            valid_records = active_records

    valid_records.sort(
        key=lambda item: item[0]
    )

    return valid_records[-1]


def _get_cached_or_fetch(
    key,
    url,
):
    cached = _cache_get(key)

    if cached is not None:
        return cached

    try:
        value = _fetch_json(url)
    except SpaceWeatherServiceError:
        stale = _cache_get_stale(key)

        if stale is not None:
            return stale

        raise

    _cache_set(key, value)

    return value


def get_space_weather_data():
    """
    Return the latest normalized NOAA SWPC
    space-weather snapshot.
    """

    wind_records = _get_cached_or_fetch(
        "solar_wind",
        _SWPC_RTSW_WIND_URL,
    )

    magnetic_records = _get_cached_or_fetch(
        "magnetic_field",
        _SWPC_RTSW_MAG_URL,
    )

    kp_records = _get_cached_or_fetch(
        "planetary_kp",
        _SWPC_KP_URL,
    )

    wind_latest = _latest_object_record(
        wind_records,
        prefer_active=True,
    )

    magnetic_latest = _latest_object_record(
        magnetic_records,
        prefer_active=True,
    )

    kp_latest = _latest_object_record(
        kp_records
    )

    if (
        wind_latest is None
        and magnetic_latest is None
        and kp_latest is None
    ):
        raise SpaceWeatherServiceError(
            "NOAA SWPC returned no valid "
            "space-weather observations."
        )

    timestamps = [
        item[0]
        for item in (
            wind_latest,
            magnetic_latest,
            kp_latest,
        )
        if item is not None
    ]

    observation_time = max(
        timestamps
    ).isoformat()

    wind = (
        wind_latest[1]
        if wind_latest is not None
        else {}
    )

    magnetic = (
        magnetic_latest[1]
        if magnetic_latest is not None
        else {}
    )

    kp = (
        kp_latest[1]
        if kp_latest is not None
        else {}
    )

    return SpaceWeatherData(
        observation_time=observation_time,
        solar_wind=SolarWind(
            speed_km_s=_to_float(
                wind.get("proton_speed")
            ),
            density_cm3=_to_float(
                wind.get("proton_density")
            ),
            temperature_k=_to_float(
                wind.get("proton_temperature")
            ),
        ),
        magnetic_field=MagneticField(
            bt_nt=_to_float(
                magnetic.get("bt")
            ),
            bz_nt=_to_float(
                magnetic.get("bz_gsm")
            ),
        ),
        geomagnetic=Geomagnetic(
            kp=_to_float(
                kp.get("Kp")
            ),
        ),
        provenance=ScientificProvenance(
            sources=(
                _SWPC_SOURCE,
            ),
            reference_frames=(
                "GSM",
            ),
        ),
    )


def get_space_weather_data_source():
    return _SWPC_SOURCE
