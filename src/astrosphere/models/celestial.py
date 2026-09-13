from dataclasses import dataclass


@dataclass(frozen=True)
class CelestialObject:
    id: str
    name: str
    object_type: str
    parent_id: str | None = None
    system_id: str | None = None
    description: str | None = None
