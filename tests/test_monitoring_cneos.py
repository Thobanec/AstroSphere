import json
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from astrosphere.monitoring.sources.cneos import (
    CNEOSMonitoringError,
    _build_url,
    fetch_cneos_close_approaches,
    normalize_cneos_event,
)


def test_build_url_contains_expected_parameters():
    url = _build_url(
        date_min="2026-01-01",
        date_max="2027-01-01",
    )

    assert url.startswith(
        "https://ssd-api.jpl.nasa.gov/cad.api?"
    )
    assert "body=Earth" in url
    assert "sort=date" in url
    assert "fullname=true" in url
    assert "date-min=2026-01-01" in url
    assert "date-max=2027-01-01" in url


def test_normalize_cneos_event():
    detected_at = datetime(
        2026,
        9,
        25,
        14,
        0,
        tzinfo=timezone.utc,
    )

    row = {
        "des": "99942",
        "cd": "2029-Apr-13 13:46",
        "dist": "0.0023",
        "dist_min": "0.0021",
        "dist_max": "0.0025",
        "v_rel": "5.86",
        "fullname": "99942 Apophis",
        "orbit_id": "123",
    }

    event = normalize_cneos_event(
        row,
        detected_at=detected_at,
    )

    assert event.event_type == (
        "asteroid_close_approach"
    )
    assert event.source == "NASA/JPL CNEOS"
    assert event.object_id == "asteroid:99942"
    assert event.object_name == "99942 Apophis"
    assert event.affected_body == "Earth"
    assert event.detected_at == detected_at
    assert event.severity == "information"

    assert event.data["designation"] == "99942"
    assert event.data["distance_au"] == 0.0023
    assert event.data["distance_min_au"] == 0.0021
    assert event.data["distance_max_au"] == 0.0025
    assert event.data["relative_velocity_km_s"] == 5.86
    assert event.data["orbit_id"] == "123"

    assert event.fingerprint
    assert event.event_id.startswith(
        "cneos-close-approach-"
    )


def test_normalize_cneos_event_fingerprint_is_stable():
    row = {
        "des": "99942",
        "cd": "2029-Apr-13 13:46",
        "dist": "0.0023",
        "dist_min": "0.0021",
        "dist_max": "0.0025",
        "v_rel": "5.86",
        "fullname": "99942 Apophis",
        "orbit_id": "123",
    }

    first = normalize_cneos_event(row)
    second = normalize_cneos_event(row)

    assert first.fingerprint == second.fingerprint
    assert first.event_id == second.event_id


def test_fetch_cneos_close_approaches():
    payload = {
        "fields": [
            "des",
            "orbit_id",
            "jd",
            "cd",
            "dist",
            "dist_min",
            "dist_max",
            "v_rel",
            "fullname",
        ],
        "data": [
            [
                "99942",
                "123",
                "2462224.0",
                "2029-Apr-13 13:46",
                "0.0023",
                "0.0021",
                "0.0025",
                "5.86",
                "99942 Apophis",
            ]
        ],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return json.dumps(payload).encode(
                "utf-8"
            )

    def fake_urlopen(*args, **kwargs):
        return FakeResponse()

    with patch(
        "urllib.request.urlopen",
        fake_urlopen,
    ):
        rows = fetch_cneos_close_approaches()

    assert len(rows) == 1
    assert rows[0]["des"] == "99942"
    assert rows[0]["fullname"] == "99942 Apophis"
    assert rows[0]["dist"] == "0.0023"
    assert rows[0]["v_rel"] == "5.86"


def test_fetch_cneos_rejects_missing_fields():
    payload = {
        "fields": [
            "des",
            "fullname",
        ],
        "data": [],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return json.dumps(payload).encode(
                "utf-8"
            )

    def fake_urlopen(*args, **kwargs):
        return FakeResponse()

    with patch(
        "urllib.request.urlopen",
        fake_urlopen,
    ):
        with pytest.raises(
            CNEOSMonitoringError,
            match="missing required fields",
        ):
            fetch_cneos_close_approaches()


def test_fetch_cneos_translates_network_failure():
    def fake_urlopen(*args, **kwargs):
        raise OSError("test network failure")

    with patch(
        "urllib.request.urlopen",
        fake_urlopen,
    ):
        with pytest.raises(
            CNEOSMonitoringError,
            match="currently unavailable",
        ):
            fetch_cneos_close_approaches()