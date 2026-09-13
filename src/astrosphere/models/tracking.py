from dataclasses import dataclass


@dataclass
class TrackingObject:
    name: str
    object_id: str
    object_type: str