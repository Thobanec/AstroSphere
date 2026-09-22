from datetime import datetime, timezone

import pytest

from astrosphere.astronomy.planetary_trajectory import (
    calculate_planetary_trajectory,
)


def test_earth_planetary_trajectory_returns_requested_samples():
    start = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    results = calculate_planetary_trajectory(
        "earth",
        observation_time=start,
        days=365,
        samples=11,
    )

    assert len(results) == 11
    assert results[0]["date"] == start
    assert results[-1]["date"] == datetime(
        2027,
        1,
        1,
        tzinfo=timezone.utc,
    )


def test_earth_planetary_trajectory_contains_ecliptic_coordinates():
    start = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    results = calculate_planetary_trajectory(
        "earth",
        observation_time=start,
        days=30,
        samples=5,
    )

    for result in results:
        assert "date" in result
        assert "x_au" in result
        assert "y_au" in result
        assert "z_au" in result

        assert isinstance(result["x_au"], float)
        assert isinstance(result["y_au"], float)
        assert isinstance(result["z_au"], float)


def test_planetary_trajectory_rejects_unknown_planet():
    with pytest.raises(ValueError, match="Unsupported planet"):
        calculate_planetary_trajectory("vulcan")


def test_planetary_trajectory_rejects_invalid_days():
    with pytest.raises(
        ValueError,
        match="days must be greater than zero",
    ):
        calculate_planetary_trajectory(
            "earth",
            days=0,
        )


def test_planetary_trajectory_rejects_too_few_samples():
    with pytest.raises(
        ValueError,
        match="samples must be at least 2",
    ):
        calculate_planetary_trajectory(
            "earth",
            samples=1,
        )
