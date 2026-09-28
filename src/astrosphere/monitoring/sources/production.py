from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

from .cneos import monitor_cneos_close_approaches
from .noaa import monitor_noaa_space_weather


DEFAULT_CNEOS_LOOKAHEAD_DAYS = 30


def build_cneos_monitoring_source(
    *,
    lookahead_days: int = DEFAULT_CNEOS_LOOKAHEAD_DAYS,
) -> Callable[[], list]:
    """Build the production CNEOS monitoring callable.

    The returned callable queries a rolling window beginning at the
    current UTC date and extending through the configured look-ahead
    period.
    """

    if lookahead_days < 0:
        raise ValueError("lookahead_days must be >= 0.")

    def source() -> list:
        now = datetime.now(timezone.utc)
        date_min = now.date().isoformat()
        date_max = (
            now.date() + timedelta(days=lookahead_days)
        ).isoformat()

        return monitor_cneos_close_approaches(
            date_min=date_min,
            date_max=date_max,
            detected_at=now,
        )

    return source


def build_noaa_monitoring_source() -> Callable[[], object]:
    """Build the production NOAA SWPC monitoring callable."""

    def source() -> object:
        return monitor_noaa_space_weather(
            detected_at=datetime.now(timezone.utc),
        )

    return source
