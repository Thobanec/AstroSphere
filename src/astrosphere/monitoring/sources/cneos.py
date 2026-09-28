from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from astrosphere.scientific.close_approaches import (
    CNEOS_CAD_URL,
)

from ..models import MonitoringEvent


class CNEOSMonitoringError(Exception):
    """Raised when the CNEOS monitoring source cannot be read."""


_REQUIRED_FIELDS = (
    "des",
    "cd",
    "dist",
    "dist_min",
    "dist_max",
    "v_rel",
    "fullname",
)


def _build_url(
    *,
    date_min: str | None = None,
    date_max: str | None = None,
) -> str:
    params: dict[str, str] = {
        "body": "Earth",
        "sort": "date",
        "fullname": "true",
    }

    if date_min:
        params["date-min"] = str(date_min)

    if date_max:
        params["date-max"] = str(date_max)

    return (
        CNEOS_CAD_URL
        + "?"
        + urllib.parse.urlencode(params)
    )


def _ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()

    try:
        import certifi

        context = ssl.create_default_context(
            cafile=certifi.where()
        )
    except ImportError:
        pass

    return context


def fetch_cneos_close_approaches(
    *,
    date_min: str | None = None,
    date_max: str | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """
    Fetch raw Earth close-approach rows from NASA/JPL CNEOS.

    This monitoring adapter intentionally does not require the
    asteroid to exist in AstroSphere's canonical registry.
    """

    url = _build_url(
        date_min=date_min,
        date_max=date_max,
    )

    try:
        with urllib.request.urlopen(
            url,
            context=_ssl_context(),
            timeout=timeout,
        ) as response:
            payload = json.load(response)

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ) as error:
        raise CNEOSMonitoringError(
            "CNEOS close-approach monitoring data "
            "is currently unavailable."
        ) from error

    fields = payload.get("fields", [])
    rows = payload.get("data", [])

    field_indexes = {
        field: fields.index(field)
        for field in _REQUIRED_FIELDS
        if field in fields
    }

    missing_fields = [
        field
        for field in _REQUIRED_FIELDS
        if field not in field_indexes
    ]

    if missing_fields:
        raise CNEOSMonitoringError(
            "CNEOS response is missing required fields: "
            + ", ".join(missing_fields)
        )

    return [
        {
            field: row[field_indexes[field]]
            for field in _REQUIRED_FIELDS
        }
        for row in rows
    ]


def normalize_cneos_event(
    row: dict[str, Any],
    *,
    detected_at: datetime | None = None,
) -> MonitoringEvent:
    """
    Convert one CNEOS close-approach row into a MonitoringEvent.
    """

    detected_at = detected_at or datetime.now(timezone.utc)

    designation = str(row["des"]).strip()
    fullname = str(row["fullname"]).strip()
    close_approach_time = str(row["cd"]).strip()

    object_id = f"asteroid:{designation}"

    fingerprint_source = "|".join(
        (
            designation,
            close_approach_time,
            str(row["dist"]),
            str(row["v_rel"]),
        )
    )

    fingerprint = sha256(
        fingerprint_source.encode("utf-8")
    ).hexdigest()

    distance_au = float(row["dist"])
    distance_min_au = float(row["dist_min"])
    distance_max_au = float(row["dist_max"])
    relative_velocity_km_s = float(row["v_rel"])

    return MonitoringEvent(
        event_id=f"cneos-close-approach-{fingerprint[:24]}",
        event_type="asteroid_close_approach",
        source="NASA/JPL CNEOS",
        detected_at=detected_at,
        object_id=object_id,
        object_name=fullname,
        affected_body="Earth",
        severity="information",
        status="active",
        summary=(
            f"{fullname} has a recorded Earth close approach "
            f"at {close_approach_time}."
        ),
        source_url=CNEOS_CAD_URL,
        data={
            "designation": designation,
            "fullname": fullname,
            "close_approach_time": close_approach_time,
            "distance_au": distance_au,
            "distance_min_au": distance_min_au,
            "distance_max_au": distance_max_au,
            "relative_velocity_km_s": (
                relative_velocity_km_s
            ),
            "orbit_id": row.get("orbit_id"),
        },
        fingerprint=fingerprint,
    )


def monitor_cneos_close_approaches(
    *,
    date_min: str | None = None,
    date_max: str | None = None,
    detected_at: datetime | None = None,
) -> list[MonitoringEvent]:
    """
    Fetch and normalize current CNEOS Earth close approaches.
    """

    rows = fetch_cneos_close_approaches(
        date_min=date_min,
        date_max=date_max,
    )

    return [
        normalize_cneos_event(
            row,
            detected_at=detected_at,
        )
        for row in rows
    ]