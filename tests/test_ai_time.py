from datetime import datetime, timezone

import pytest

from astrosphere.ai.time import normalize_observation_time


def test_normalize_observation_time_none():
    assert normalize_observation_time(None) is None


def test_normalize_observation_time_iso_z():
    result = normalize_observation_time(
        "2026-01-01T00:00:00Z"
    )

    assert result == datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )


def test_normalize_observation_time_iso_offset():
    result = normalize_observation_time(
        "2026-01-01T02:00:00+02:00"
    )

    assert result == datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )


def test_normalize_observation_time_datetime():
    value = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    assert normalize_observation_time(value) == value


def test_normalize_observation_time_rejects_invalid_string():
    with pytest.raises(
        ValueError,
        match="valid ISO-8601",
    ):
        normalize_observation_time("not-a-date")


def test_normalize_observation_time_rejects_empty_string():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        normalize_observation_time("")


def test_normalize_observation_time_rejects_invalid_type():
    with pytest.raises(
        ValueError,
        match="datetime or ISO-8601 string",
    ):
        normalize_observation_time(12345)
