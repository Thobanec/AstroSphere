from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from astrosphere.auth.database import get_connection
from astrosphere.auth.rbac import organization_user_has_permission
from astrosphere.auth.models import User
from astrosphere.auth.service import (
    UserAlreadyExistsError,
    _create_user_with_connection,
)


ORGANIZATION_TYPES = (
    "SCHOOL",
    "UNIVERSITY",
    "SCIENCE_CENTRE",
    "PLANETARIUM",
    "ASTRONOMY_ORGANISATION",
    "OTHER",
)

MEMBERSHIP_ACTIVE = "active"
MEMBERSHIP_SUSPENDED = "suspended"
MEMBERSHIP_PENDING = "pending"

ORGANIZATION_ASSIGNABLE_ROLES = (
    "educator",
    "researcher",
    "learner",
)


class OrganizationAlreadyExistsError(ValueError):
    """Raised when an organization name or slug already exists."""


class OrganizationNotFoundError(ValueError):
    """Raised when an organization cannot be found."""


class MembershipAlreadyExistsError(ValueError):
    """Raised when a user is already a member of an organization."""


class MembershipNotFoundError(ValueError):
    """Raised when an organization membership cannot be found."""


class OrganizationUserCreationError(ValueError):
    """Raised when an organization user cannot be created."""


@dataclass(frozen=True)
class Organization:
    id: int
    name: str
    slug: str
    organization_type: str
    is_active: bool
    created_at: datetime
    created_by: Optional[int]


@dataclass(frozen=True)
class OrganizationMembership:
    id: int
    organization_id: int
    user_id: int
    status: str
    joined_at: datetime
    created_at: datetime


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def _row_to_organization(row) -> Organization:
    return Organization(
        id=int(row["id"]),
        name=row["name"],
        slug=row["slug"],
        organization_type=row["organization_type"],
        is_active=bool(row["is_active"]),
        created_at=_parse_datetime(row["created_at"]),
        created_by=(
            int(row["created_by"])
            if row["created_by"] is not None
            else None
        ),
    )


def _row_to_membership(row) -> OrganizationMembership:
    return OrganizationMembership(
        id=int(row["id"]),
        organization_id=int(row["organization_id"]),
        user_id=int(row["user_id"]),
        status=row["status"],
        joined_at=_parse_datetime(row["joined_at"]),
        created_at=_parse_datetime(row["created_at"]),
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_slug(slug: str) -> str:
    normalized = slug.strip().lower()

    if not normalized:
        raise ValueError("Organization slug is required.")

    return normalized


def _validate_organization_type(organization_type: str) -> str:
    normalized = organization_type.strip().upper()

    if normalized not in ORGANIZATION_TYPES:
        raise ValueError(
            f"Unsupported organization type: {organization_type}"
        )

    return normalized


def create_organization(
    *,
    name: str,
    slug: str,
    organization_type: str,
    created_by: Optional[int] = None,
) -> Organization:
    name = name.strip()
    slug = _normalize_slug(slug)
    organization_type = _validate_organization_type(organization_type)

    if not name:
        raise ValueError("Organization name is required.")

    now = _utc_now()

    with get_connection() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO organizations (
                    name,
                    slug,
                    organization_type,
                    is_active,
                    created_at,
                    created_by
                )
                VALUES (?, ?, ?, 1, ?, ?)
                """,
                (
                    name,
                    slug,
                    organization_type,
                    now,
                    created_by,
                ),
            )
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                raise OrganizationAlreadyExistsError(
                    "An organization with this name or slug already exists."
                ) from exc
            raise

        organization_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT
                id,
                name,
                slug,
                organization_type,
                is_active,
                created_at,
                created_by
            FROM organizations
            WHERE id = ?
            """,
            (organization_id,),
        ).fetchone()

    if row is None:
        raise OrganizationNotFoundError(
            "The organization was created but could not be retrieved."
        )

    return _row_to_organization(row)


def get_organization(organization_id: int) -> Optional[Organization]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                slug,
                organization_type,
                is_active,
                created_at,
                created_by
            FROM organizations
            WHERE id = ?
            """,
            (organization_id,),
        ).fetchone()

    return _row_to_organization(row) if row else None


def get_organization_by_slug(slug: str) -> Optional[Organization]:
    slug = _normalize_slug(slug)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                slug,
                organization_type,
                is_active,
                created_at,
                created_by
            FROM organizations
            WHERE slug = ?
            """,
            (slug,),
        ).fetchone()

    return _row_to_organization(row) if row else None


def get_all_organizations() -> list[Organization]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                slug,
                organization_type,
                is_active,
                created_at,
                created_by
            FROM organizations
            ORDER BY created_at ASC, id ASC
            """
        ).fetchall()

    return [_row_to_organization(row) for row in rows]


def set_organization_status(
    organization_id: int,
    is_active: bool,
) -> Organization:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE organizations
            SET is_active = ?
            WHERE id = ?
            """,
            (
                int(is_active),
                organization_id,
            ),
        )

        if cursor.rowcount == 0:
            raise OrganizationNotFoundError(
                "Organization was not found."
            )

        row = connection.execute(
            """
            SELECT
                id,
                name,
                slug,
                organization_type,
                is_active,
                created_at,
                created_by
            FROM organizations
            WHERE id = ?
            """,
            (organization_id,),
        ).fetchone()

    return _row_to_organization(row)


def add_organization_member(
    *,
    organization_id: int,
    user_id: int,
    status: str = MEMBERSHIP_ACTIVE,
) -> OrganizationMembership:
    status = status.strip().lower()

    if status not in {
        MEMBERSHIP_ACTIVE,
        MEMBERSHIP_SUSPENDED,
        MEMBERSHIP_PENDING,
    }:
        raise ValueError(f"Unsupported membership status: {status}")

    now = _utc_now()

    with get_connection() as connection:
        organization = connection.execute(
            """
            SELECT id
            FROM organizations
            WHERE id = ?
            """,
            (organization_id,),
        ).fetchone()

        if organization is None:
            raise OrganizationNotFoundError(
                "Organization was not found."
            )

        user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            raise ValueError("User was not found.")

        existing = connection.execute(
            """
            SELECT id
            FROM organization_memberships
            WHERE organization_id = ?
              AND user_id = ?
            """,
            (
                organization_id,
                user_id,
            ),
        ).fetchone()

        if existing is not None:
            raise MembershipAlreadyExistsError(
                "The user is already a member of this organization."
            )

        cursor = connection.execute(
            """
            INSERT INTO organization_memberships (
                organization_id,
                user_id,
                status,
                joined_at,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                organization_id,
                user_id,
                status,
                now,
                now,
            ),
        )

        membership_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT
                id,
                organization_id,
                user_id,
                status,
                joined_at,
                created_at
            FROM organization_memberships
            WHERE id = ?
            """,
            (membership_id,),
        ).fetchone()

    if row is None:
        raise MembershipNotFoundError(
            "The membership was created but could not be retrieved."
        )

    return _row_to_membership(row)


def get_membership(
    *,
    organization_id: int,
    user_id: int,
) -> Optional[OrganizationMembership]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                organization_id,
                user_id,
                status,
                joined_at,
                created_at
            FROM organization_memberships
            WHERE organization_id = ?
              AND user_id = ?
            """,
            (
                organization_id,
                user_id,
            ),
        ).fetchone()

    return _row_to_membership(row) if row else None


def get_user_memberships(
    user_id: int,
) -> list[OrganizationMembership]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                organization_id,
                user_id,
                status,
                joined_at,
                created_at
            FROM organization_memberships
            WHERE user_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (user_id,),
        ).fetchall()

    return [_row_to_membership(row) for row in rows]


def get_organization_members(
    organization_id: int,
) -> list[OrganizationMembership]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                organization_id,
                user_id,
                status,
                joined_at,
                created_at
            FROM organization_memberships
            WHERE organization_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (organization_id,),
        ).fetchall()

    return [_row_to_membership(row) for row in rows]


def remove_organization_member(
    *,
    organization_id: int,
    user_id: int,
) -> None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM organization_memberships
            WHERE organization_id = ?
              AND user_id = ?
            """,
            (
                organization_id,
                user_id,
            ),
        )

        if cursor.rowcount == 0:
            raise MembershipNotFoundError(
                "The organization membership was not found."
            )


def get_assignable_organization_roles() -> list[dict]:
    """Return roles that organization administrators may assign."""
    placeholders = ", ".join(
        "?" for _ in ORGANIZATION_ASSIGNABLE_ROLES
    )

    with get_connection() as connection:
        rows = connection.execute(
            f"""
            SELECT
                id,
                name,
                description,
                is_system_role,
                created_at
            FROM roles
            WHERE name IN ({placeholders})
            ORDER BY
                CASE name
                    WHEN 'learner' THEN 1
                    WHEN 'educator' THEN 2
                    WHEN 'researcher' THEN 3
                    ELSE 99
                END
            """,
            ORGANIZATION_ASSIGNABLE_ROLES,
        ).fetchall()

    return [dict(row) for row in rows]


def get_organization_role_by_name(role_name: str) -> dict | None:
    """Return an organization role by its allowed role name."""
    normalized = role_name.strip().lower()

    if normalized not in ORGANIZATION_ASSIGNABLE_ROLES:
        return None

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                description,
                is_system_role,
                created_at
            FROM roles
            WHERE name = ?
            """,
            (normalized,),
        ).fetchone()

    return dict(row) if row else None

def create_organization_user(
    *,
    organization_id: int,
    created_by: int,
    email: str,
    username: str,
    display_name: str,
    password: str,
    organization_role: str,
) -> User:
    """Create a user, organization membership, and organization role atomically."""

    role = get_organization_role_by_name(organization_role)

    if role is None:
        raise OrganizationUserCreationError(
            "Invalid organization role. Allowed roles are: "
            + ", ".join(ORGANIZATION_ASSIGNABLE_ROLES)
            + "."
        )

    if not organization_user_has_permission(
        created_by,
        organization_id,
        "users.create",
    ):
        raise OrganizationUserCreationError(
            "The creating user does not have permission to create users "
            "in this organization."
        )

    now = _utc_now()

    with get_connection() as connection:
        try:
            organization = connection.execute(
                """
                SELECT id, is_active
                FROM organizations
                WHERE id = ?
                """,
                (organization_id,),
            ).fetchone()

            if organization is None:
                raise OrganizationUserCreationError(
                    "The organization was not found."
                )

            if not bool(organization["is_active"]):
                raise OrganizationUserCreationError(
                    "The organization is inactive."
                )

            user = _create_user_with_connection(
                connection,
                email=email,
                username=username,
                display_name=display_name,
                password=password,
                created_by=created_by,
            )

            cursor = connection.execute(
                """
                INSERT INTO organization_memberships (
                    organization_id,
                    user_id,
                    status,
                    joined_at,
                    created_at
                )
                VALUES (?, ?, 'active', ?, ?)
                """,
                (
                    organization_id,
                    user.id,
                    now,
                    now,
                ),
            )

            membership_id = cursor.lastrowid

            if membership_id is None:
                raise OrganizationUserCreationError(
                    "The organization membership could not be created."
                )

            connection.execute(
                """
                INSERT INTO organization_membership_roles (
                    membership_id,
                    role_id,
                    assigned_at,
                    assigned_by
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    membership_id,
                    role["id"],
                    now,
                    created_by,
                ),
            )

            connection.commit()

            return user

        except UserAlreadyExistsError:
            connection.rollback()
            raise OrganizationUserCreationError(
                "A user with the supplied email or username already exists."
            )

        except OrganizationUserCreationError:
            connection.rollback()
            raise

        except Exception as exc:
            connection.rollback()
            raise OrganizationUserCreationError(
                "The organization user could not be created."
            ) from exc

def assign_organization_role(
    *,
    membership_id: int,
    role_id: int,
    assigned_by: Optional[int] = None,
) -> None:
    now = _utc_now()

    with get_connection() as connection:
        membership = connection.execute(
            """
            SELECT id
            FROM organization_memberships
            WHERE id = ?
            """,
            (membership_id,),
        ).fetchone()

        if membership is None:
            raise MembershipNotFoundError(
                "The organization membership was not found."
            )

        role = connection.execute(
            """
            SELECT id
            FROM roles
            WHERE id = ?
            """,
            (role_id,),
        ).fetchone()

        if role is None:
            raise ValueError("Role was not found.")

        connection.execute(
            """
            INSERT OR IGNORE INTO organization_membership_roles (
                membership_id,
                role_id,
                assigned_at,
                assigned_by
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                membership_id,
                role_id,
                now,
                assigned_by,
            ),
        )


def remove_organization_role(
    *,
    membership_id: int,
    role_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM organization_membership_roles
            WHERE membership_id = ?
              AND role_id = ?
            """,
            (
                membership_id,
                role_id,
            ),
        )


def get_membership_roles(
    membership_id: int,
) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                roles.id,
                roles.name,
                roles.description,
                roles.is_system_role,
                roles.created_at
            FROM organization_membership_roles AS membership_roles
            INNER JOIN roles
                ON roles.id = membership_roles.role_id
            WHERE membership_roles.membership_id = ?
            ORDER BY roles.name ASC
            """,
            (membership_id,),
        ).fetchall()

    return [dict(row) for row in rows]
