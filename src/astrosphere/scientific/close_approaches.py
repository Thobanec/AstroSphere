from datetime import datetime, timedelta, timezone
import json
import ssl
import threading
import urllib.error
import urllib.parse
import urllib.request

from astrosphere.models.celestial_registry import (
    get_celestial_object,
)
from astrosphere.models.close_approach import (
    CloseApproach,
)
from astrosphere.models.scientific import (
    DataSource,
)


CNEOS_CAD_URL = (
    "https://ssd-api.jpl.nasa.gov/cad.api"
)

AU_KM = 149597870.7

_CNEOS_CACHE_TTL = timedelta(hours=1)

_CNEOS_CACHE = {}

_CNEOS_CACHE_LOCK = threading.Lock()


class CloseApproachServiceError(Exception):
    """
    Raised when the CNEOS close-approach service
    cannot provide fresh data.
    """


_CNEOS_SOURCE = DataSource(
    name="NASA/JPL SBDB Close Approach Data API",
    provider="NASA/JPL CNEOS",
    url=CNEOS_CAD_URL,
    dataset="SBDB Close Approach Data",
)


def _cache_key(
    designation,
    date_min,
    date_max,
):
    return (
        str(designation).strip(),
        str(date_min) if date_min else None,
        str(date_max) if date_max else None,
    )


def _get_cached_result(key):
    with _CNEOS_CACHE_LOCK:
        entry = _CNEOS_CACHE.get(key)

    if entry is None:
        return None, False

    cached_at, results = entry

    age = (
        datetime.now(timezone.utc)
        - cached_at
    )

    return results, age <= _CNEOS_CACHE_TTL


def _store_cached_result(key, results):
    with _CNEOS_CACHE_LOCK:
        _CNEOS_CACHE[key] = (
            datetime.now(timezone.utc),
            results,
        )


def get_close_approach_data(
    designation,
    date_min=None,
    date_max=None,
):
    """
    Return close-approach events for a canonical asteroid.
    """

    designation = str(
        designation
    ).strip()

    if not designation:
        raise ValueError(
            "Asteroid designation cannot be empty."
        )

    key = _cache_key(
        designation,
        date_min,
        date_max,
    )

    cached_results, cache_is_fresh = (
        _get_cached_result(key)
    )

    if cache_is_fresh:
        return cached_results

    params = {
        "des": designation,
        "body": "Earth",
        "sort": "date",
        "fullname": "true",
    }

    if date_min:
        params["date-min"] = str(
            date_min
        )

    if date_max:
        params["date-max"] = str(
            date_max
        )

    url = (
        CNEOS_CAD_URL
        + "?"
        + urllib.parse.urlencode(
            params
        )
    )

    context = ssl.create_default_context()

    try:

        import certifi

        context = ssl.create_default_context(
            cafile=certifi.where()
        )

    except ImportError:
        pass

    try:

        with urllib.request.urlopen(
            url,
            context=context,
            timeout=30,
        ) as response:

            payload = json.load(
                response
            )

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ) as error:

        if cached_results is not None:
            return cached_results

        raise CloseApproachServiceError(
            "CNEOS close-approach data is "
            "currently unavailable."
        ) from error

    fields = payload.get(
        "fields",
        [],
    )

    rows = payload.get(
        "data",
        [],
    )

    field_indexes = {
        field: fields.index(field)
        for field in (
            "des",
            "orbit_id",
            "jd",
            "cd",
            "dist",
            "dist_min",
            "dist_max",
            "v_rel",
            "fullname",
        )
        if field in fields
    }

    required_fields = (
        "des",
        "cd",
        "dist",
        "dist_min",
        "dist_max",
        "v_rel",
        "fullname",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in field_indexes
    ]

    if missing_fields:
        raise ValueError(
            "CNEOS response is missing "
            "required fields: "
            + ", ".join(
                missing_fields
            )
        )

    results = []

    for row in rows:

        object_designation = str(
            row[field_indexes["des"]]
        )

        fullname = str(
            row[field_indexes["fullname"]]
        )

        permanent_designation = (
            object_designation
            if object_designation.isdigit()
            else object_designation
        )

        object_id = (
            "asteroid:"
            + permanent_designation
        )

        obj = get_celestial_object(
            object_id
        )

        if obj is None:
            raise ValueError(
                "Asteroid is not registered "
                "as a canonical celestial object: "
                + object_id
            )

        distance_au = float(
            row[field_indexes["dist"]]
        )

        distance_min_au = float(
            row[field_indexes["dist_min"]]
        )

        distance_max_au = float(
            row[field_indexes["dist_max"]]
        )

        results.append(
            CloseApproach(
                object_id=obj.id,
                designation=object_designation,
                fullname=fullname,
                close_approach_time=str(
                    row[field_indexes["cd"]]
                ),
                distance_au=distance_au,
                distance_min_au=distance_min_au,
                distance_max_au=distance_max_au,
                distance_km=(
                    distance_au * AU_KM
                ),
                distance_min_km=(
                    distance_min_au * AU_KM
                ),
                distance_max_km=(
                    distance_max_au * AU_KM
                ),
                relative_velocity_km_s=float(
                    row[field_indexes["v_rel"]]
                ),
                orbit_id=(
                    str(
                        row[field_indexes["orbit_id"]]
                    )
                    if "orbit_id" in field_indexes
                    else None
                ),
                source=_CNEOS_SOURCE,
            )
        )

    _store_cached_result(
        key,
        results,
    )

    return results


def get_cneos_data_source():
    """
    Return CNEOS close-approach data source metadata.
    """

    return _CNEOS_SOURCE
