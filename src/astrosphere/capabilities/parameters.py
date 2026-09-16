from datetime import datetime

from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_SPACE_WEATHER,
    CAPABILITY_TRACKING,
    CAPABILITY_TRAJECTORY,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)


def _validate_iso_datetime(value, field_name):
    if value is None:
        return

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be an ISO 8601 string."
        )

    try:
        datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a valid ISO 8601 datetime."
        ) from exc


def _validate_iso_date(value, field_name):
    if value is None:
        return

    if not isinstance(value, str):
        raise ValueError(
            f"{field_name} must be an ISO 8601 date."
        )

    try:
        datetime.strptime(
            value,
            "%Y-%m-%d",
        )
    except ValueError as exc:
        raise ValueError(
            f"{field_name} must be a valid YYYY-MM-DD date."
        ) from exc


def _validate_parameters_dict(parameters):
    if parameters is None:
        return {}

    if not isinstance(parameters, dict):
        raise ValueError(
            "Capability parameters must be an object."
        )

    return parameters


def validate_capability_parameters(
    capability_id,
    parameters=None,
):
    parameters = _validate_parameters_dict(
        parameters
    )

    if capability_id == CAPABILITY_TRACKING:
        allowed = {
            "observation_time",
        }

    elif capability_id == CAPABILITY_TRAJECTORY:
        allowed = {
            "samples",
            "observation_time",
        }

        samples = parameters.get("samples")

        if samples is not None:
            if not isinstance(samples, int):
                raise ValueError(
                    "Trajectory samples must be an integer."
                )

            if samples < 2:
                raise ValueError(
                    "Trajectory samples must be at least 2."
                )

    elif capability_id == CAPABILITY_CLOSE_APPROACHES:
        allowed = {
            "date_min",
            "date_max",
        }

        _validate_iso_date(
            parameters.get("date_min"),
            "date_min",
        )

        _validate_iso_date(
            parameters.get("date_max"),
            "date_max",
        )

        date_min = parameters.get("date_min")
        date_max = parameters.get("date_max")

        if (
            date_min is not None
            and date_max is not None
            and date_min > date_max
        ):
            raise ValueError(
                "date_min must be earlier than or equal to date_max."
            )

    elif capability_id == CAPABILITY_SPACE_WEATHER:
        allowed = {
            "observation_time",
        }

    elif capability_id == CAPABILITY_ORBITAL_ANALYSIS:
        allowed = {
            "reference_body",
            "target_body",
            "start_date",
            "months",
            "interval_days",
        }

        reference_body = parameters.get(
            "reference_body"
        )
        target_body = parameters.get(
            "target_body"
        )

        if not reference_body:
            raise ValueError(
                "reference_body is required."
            )

        if not target_body:
            raise ValueError(
                "target_body is required."
            )

        reference_object = get_celestial_object(
            reference_body.strip().lower()
            if isinstance(reference_body, str)
            else reference_body
        )

        if reference_object is None:
            raise ValueError(
                f"Unknown reference body: {reference_body}"
            )

        target_object = get_celestial_object(
            target_body.strip().lower()
            if isinstance(target_body, str)
            else target_body
        )

        if target_object is None:
            raise ValueError(
                f"Unknown target body: {target_body}"
            )

        _validate_iso_date(
            parameters.get("start_date"),
            "start_date",
        )

        months = parameters.get("months")

        if months is not None:
            if not isinstance(months, int):
                raise ValueError(
                    "Orbital-analysis months must be an integer."
                )

            if months < 1:
                raise ValueError(
                    "Orbital-analysis months must be at least 1."
                )

        interval_days = parameters.get(
            "interval_days"
        )

        if interval_days is not None:
            if not isinstance(interval_days, int):
                raise ValueError(
                    "Orbital-analysis interval_days "
                    "must be an integer."
                )

            if interval_days < 1:
                raise ValueError(
                    "Orbital-analysis interval_days "
                    "must be at least 1."
                )

    else:
        allowed = set()

    unexpected = set(parameters) - allowed

    if unexpected:
        names = ", ".join(
            sorted(unexpected)
        )

        raise ValueError(
            f"Unsupported parameters for "
            f"capability '{capability_id}': {names}"
        )

    return parameters
