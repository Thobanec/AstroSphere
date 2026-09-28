from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: int
    email: str
    username: str
    display_name: str
    password_hash: str
    is_active: bool
    created_at: datetime
    created_by: int | None = None
    last_login_at: datetime | None = None
