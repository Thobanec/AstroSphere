from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from .database import get_connection


SUPER_ADMINISTRATOR = "super_administrator"
FULL_ADMINISTRATOR = "full_administrator"
STANDARD_USER = "standard_user"


ORGANIZATION_ADMINISTRATOR = "organization_administrator"
EDUCATOR = "educator"
RESEARCHER = "researcher"
LEARNER = "learner"


INITIAL_ROLES = {
    SUPER_ADMINISTRATOR: (
        "Super Administrator",
        "AstroSphere platform owner with unrestricted access.",
    ),
    FULL_ADMINISTRATOR: (
        "Full Administrator",
        "Full operational administration without Super Administrator ownership controls.",
    ),
    STANDARD_USER: (
        "Standard User",
        "Standard AstroSphere user.",
    ),
}


INITIAL_ORGANIZATION_ROLES = {
    ORGANIZATION_ADMINISTRATOR: (
        "Organization Administrator",
        "Administrator for a single AstroSphere organization.",
    ),
    EDUCATOR: (
        "Educator",
        "Teacher, lecturer, or educational facilitator within an organization.",
    ),
    RESEARCHER: (
        "Researcher",
        "Research-oriented AstroSphere user within an organization.",
    ),
    LEARNER: (
        "Learner",
        "Student or learner within an AstroSphere organization.",
    ),
}

INITIAL_PERMISSIONS = {
    "users.view": "View user accounts.",
    "users.create": "Create user accounts.",
    "users.update": "Update user accounts.",
    "users.disable": "Enable or disable user accounts.",
    "users.delete": "Delete user accounts.",
    "roles.view": "View roles.",
    "roles.assign": "Assign roles to users.",
    "roles.manage": "Create and manage roles.",
    "permissions.view": "View permissions.",
    "permissions.manage": "Manage role permissions.",
    "monitoring.view": "View space monitoring.",
    "monitoring.manage": "Manage space monitoring.",
    "astronomy.view": "View astronomy data.",
    "astronomy.analyze": "Perform astronomy analysis.",
    "ai.use": "Use AstroSphere AI.",
    "content.manage": "Manage AstroSphere content.",
    "system.configure": "Configure AstroSphere system settings.",
    "audit.view": "View administrative audit logs.",
}


FULL_ADMIN_PERMISSIONS = {
    "users.view",
    "users.create",
    "users.update",
    "users.disable",
    "roles.view",
    "roles.assign",
    "permissions.view",
    "monitoring.view",
    "monitoring.manage",
    "astronomy.view",
    "astronomy.analyze",
    "ai.use",
    "content.manage",
    "audit.view",
}


STANDARD_USER_PERMISSIONS = {
    "astronomy.view",
    "astronomy.analyze",
    "ai.use",
    "monitoring.view",
}


ORGANIZATION_ADMIN_PERMISSIONS = {
    "users.view",
    "users.create",
    "users.update",
    "users.disable",
    "roles.view",
    "roles.assign",
    "monitoring.view",
    "monitoring.manage",
    "astronomy.view",
    "astronomy.analyze",
    "ai.use",
    "audit.view",
}


EDUCATOR_PERMISSIONS = {
    "astronomy.view",
    "astronomy.analyze",
    "ai.use",
    "monitoring.view",
}


RESEARCHER_PERMISSIONS = {
    "astronomy.view",
    "astronomy.analyze",
    "ai.use",
    "monitoring.view",
    "monitoring.manage",
}


LEARNER_PERMISSIONS = {
    "astronomy.view",
    "astronomy.analyze",
    "ai.use",
    "monitoring.view",
}


ORGANIZATION_ROLE_PERMISSIONS = {
    ORGANIZATION_ADMINISTRATOR: ORGANIZATION_ADMIN_PERMISSIONS,
    EDUCATOR: EDUCATOR_PERMISSIONS,
    RESEARCHER: RESEARCHER_PERMISSIONS,
    LEARNER: LEARNER_PERMISSIONS,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_rbac() -> None:
    now = _utc_now()

    with get_connection() as connection:
        for role_key, (name, description) in INITIAL_ROLES.items():
            connection.execute(
                """
                INSERT OR IGNORE INTO roles (
                    name,
                    description,
                    is_system_role,
                    created_at
                )
                VALUES (?, ?, 1, ?)
                """,
                (role_key, description, now),
            )

        for name, description in INITIAL_PERMISSIONS.items():
            connection.execute(
                """
                INSERT OR IGNORE INTO permissions (
                    name,
                    description,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (name, description, now),
            )

        for role_key, (name, description) in INITIAL_ORGANIZATION_ROLES.items():
            connection.execute(
                """
                INSERT OR IGNORE INTO roles (
                    name,
                    description,
                    is_system_role,
                    created_at
                )
                VALUES (?, ?, 1, ?)
                """,
                (role_key, description, now),
            )

        connection.commit()

        super_role = connection.execute(
            "SELECT id FROM roles WHERE name = ?",
            (SUPER_ADMINISTRATOR,),
        ).fetchone()

        full_admin_role = connection.execute(
            "SELECT id FROM roles WHERE name = ?",
            (FULL_ADMINISTRATOR,),
        ).fetchone()

        standard_role = connection.execute(
            "SELECT id FROM roles WHERE name = ?",
            (STANDARD_USER,),
        ).fetchone()

        all_permissions = connection.execute(
            "SELECT id, name FROM permissions"
        ).fetchall()

        permission_ids = {
            row["name"]: row["id"]
            for row in all_permissions
        }

        for permission in permission_ids.values():
            connection.execute(
                """
                INSERT OR IGNORE INTO role_permissions (
                    role_id,
                    permission_id,
                    assigned_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    super_role["id"],
                    permission,
                    now,
                ),
            )

        for permission_name in FULL_ADMIN_PERMISSIONS:
            connection.execute(
                """
                INSERT OR IGNORE INTO role_permissions (
                    role_id,
                    permission_id,
                    assigned_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    full_admin_role["id"],
                    permission_ids[permission_name],
                    now,
                ),
            )

        for permission_name in STANDARD_USER_PERMISSIONS:
            connection.execute(
                """
                INSERT OR IGNORE INTO role_permissions (
                    role_id,
                    permission_id,
                    assigned_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    standard_role["id"],
                    permission_ids[permission_name],
                    now,
                ),
            )

        organization_roles = connection.execute(
            """
            SELECT id, name
            FROM roles
            WHERE name IN (?, ?, ?, ?)
            """,
            (
                ORGANIZATION_ADMINISTRATOR,
                EDUCATOR,
                RESEARCHER,
                LEARNER,
            ),
        ).fetchall()

        organization_role_ids = {
            row["name"]: row["id"]
            for row in organization_roles
        }

        for role_name, permission_names in ORGANIZATION_ROLE_PERMISSIONS.items():
            role_id = organization_role_ids[role_name]

            for permission_name in permission_names:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO role_permissions (
                        role_id,
                        permission_id,
                        assigned_at
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        role_id,
                        permission_ids[permission_name],
                        now,
                    ),
                )

        connection.commit()


def get_role(role_name: str):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM roles
            WHERE name = ?
            """,
            (role_name,),
        ).fetchone()


def get_user_roles(user_id: int) -> list:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT r.*
            FROM roles r
            INNER JOIN user_roles ur
                ON ur.role_id = r.id
            WHERE ur.user_id = ?
            ORDER BY r.name
            """,
            (user_id,),
        ).fetchall()


def assign_role(
    user_id: int,
    role_name: str,
    assigned_by: int | None = None,
) -> None:
    if role_name == SUPER_ADMINISTRATOR:
        raise PermissionError(
            "Super Administrator must be assigned through the protected bootstrap process."
        )

    role = get_role(role_name)

    if role is None:
        raise ValueError(f"Unknown role: {role_name}")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO user_roles (
                user_id,
                role_id,
                assigned_at,
                assigned_by
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                role["id"],
                _utc_now(),
                assigned_by,
            ),
        )

        connection.commit()


def is_super_administrator(user_id: int) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM user_roles ur
            INNER JOIN roles r
                ON r.id = ur.role_id
            WHERE ur.user_id = ?
              AND r.name = ?
            LIMIT 1
            """,
            (
                user_id,
                SUPER_ADMINISTRATOR,
            ),
        ).fetchone()

    return row is not None


def user_has_permission(
    user_id: int,
    permission_name: str,
) -> bool:
    if is_super_administrator(user_id):
        return True

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM user_roles ur
            INNER JOIN role_permissions rp
                ON rp.role_id = ur.role_id
            INNER JOIN permissions p
                ON p.id = rp.permission_id
            WHERE ur.user_id = ?
              AND p.name = ?
            LIMIT 1
            """,
            (
                user_id,
                permission_name,
            ),
        ).fetchone()

    return row is not None


def get_user_permissions(user_id: int) -> set[str]:
    if is_super_administrator(user_id):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT name FROM permissions"
            ).fetchall()

        return {row["name"] for row in rows}

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT p.name
            FROM user_roles ur
            INNER JOIN role_permissions rp
                ON rp.role_id = ur.role_id
            INNER JOIN permissions p
                ON p.id = rp.permission_id
            WHERE ur.user_id = ?
            ORDER BY p.name
            """,
            (user_id,),
        ).fetchall()

    return {row["name"] for row in rows}







def get_organization_membership_roles(
    user_id: int,
    organization_id: int,
) -> list:
    """Return roles assigned to a user's active organization membership."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                r.*
            FROM organization_memberships om
            INNER JOIN organization_membership_roles omr
                ON omr.membership_id = om.id
            INNER JOIN roles r
                ON r.id = omr.role_id
            WHERE om.user_id = ?
              AND om.organization_id = ?
              AND om.status = 'active'
            ORDER BY r.name
            """,
            (
                user_id,
                organization_id,
            ),
        ).fetchall()

    return rows


def organization_user_has_permission(
    user_id: int,
    organization_id: int,
    permission_name: str,
) -> bool:
    """Check whether a user has a permission within an organization."""

    if is_super_administrator(user_id):
        return True

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM organization_memberships om
            INNER JOIN organization_membership_roles omr
                ON omr.membership_id = om.id
            INNER JOIN role_permissions rp
                ON rp.role_id = omr.role_id
            INNER JOIN permissions p
                ON p.id = rp.permission_id
            WHERE om.user_id = ?
              AND om.organization_id = ?
              AND om.status = 'active'
              AND p.name = ?
            LIMIT 1
            """,
            (
                user_id,
                organization_id,
                permission_name,
            ),
        ).fetchone()

    return row is not None


def get_organization_user_permissions(
    user_id: int,
    organization_id: int,
) -> set[str]:
    """Return permissions available to a user within an organization."""

    if is_super_administrator(user_id):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT name FROM permissions"
            ).fetchall()

        return {row["name"] for row in rows}

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT p.name
            FROM organization_memberships om
            INNER JOIN organization_membership_roles omr
                ON omr.membership_id = om.id
            INNER JOIN role_permissions rp
                ON rp.role_id = omr.role_id
            INNER JOIN permissions p
                ON p.id = rp.permission_id
            WHERE om.user_id = ?
              AND om.organization_id = ?
              AND om.status = 'active'
            ORDER BY p.name
            """,
            (
                user_id,
                organization_id,
            ),
        ).fetchall()

    return {row["name"] for row in rows}
