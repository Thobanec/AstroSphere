from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MONITORING_DATABASE = (
    PROJECT_ROOT / "data" / "monitoring.db"
)


def get_monitoring_database_path() -> Path:
    """Return the configured monitoring SQLite database path."""

    configured_path = os.getenv(
        "ASTROSPHERE_MONITORING_DATABASE"
    )

    if configured_path:
        return Path(configured_path).expanduser()

    return DEFAULT_MONITORING_DATABASE