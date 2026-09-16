from datetime import datetime, timezone


def normalize_observation_time(observation_time):
    if observation_time is None:
        return None

    if isinstance(observation_time, datetime):
        if observation_time.tzinfo is None:
            return observation_time.replace(tzinfo=timezone.utc)
        return observation_time.astimezone(timezone.utc)

    if isinstance(observation_time, str):
        value = observation_time.strip()

        if not value:
            raise ValueError("Observation time cannot be empty.")

        if value.endswith("Z"):
            value = value[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                "Observation time must be a valid ISO-8601 datetime."
            ) from exc

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed.astimezone(timezone.utc)

    raise ValueError(
        "Observation time must be a datetime or ISO-8601 string."
    )
