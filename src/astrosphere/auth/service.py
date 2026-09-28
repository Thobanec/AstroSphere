from __future__ import annotations

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .database import get_connection
from .models import User
from .rbac import (
    EDUCATOR,
    FULL_ADMINISTRATOR,
    LEARNER,
    ORGANIZATION_ADMINISTRATOR,
    RESEARCHER,
    STANDARD_USER,
    SUPER_ADMINISTRATOR,
    assign_role,
)
from .security import (
    build_totp_uri,
    decrypt_mfa_secret,
    encrypt_mfa_secret,
    generate_mfa_secret,
    generate_recovery_codes,
    hash_recovery_code,
    utc_now,
    verify_totp_code,
)


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    return datetime.fromisoformat(value)


def _row_to_user(row) -> User:
    return User(
        id=row["id"],
        email=row["email"],
        username=row["username"],
        display_name=row["display_name"],
        password_hash=row["password_hash"],
        is_active=bool(row["is_active"]),
        created_at=_parse_datetime(row["created_at"]),
        created_by=row["created_by"],
        last_login_at=_parse_datetime(row["last_login_at"]),
    )


def _create_user_with_connection(
    connection,
    *,
    email: str,
    username: str,
    display_name: str,
    password: str,
    created_by: int | None = None,
) -> User:
    """Create a user using an existing database transaction."""
    email = email.strip().lower()
    username = username.strip().lower()
    display_name = display_name.strip()

    if not email:
        raise ValueError("Email is required.")

    if not username:
        raise ValueError("Username is required.")

    if not display_name:
        raise ValueError("Display name is required.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")

    now = datetime.now(timezone.utc).isoformat()
    password_hash = generate_password_hash(password)

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (
                email,
                username,
                display_name,
                password_hash,
                is_active,
                created_at,
                created_by
            )
            VALUES (?, ?, ?, ?, 1, ?, ?)
            """,
            (
                email,
                username,
                display_name,
                password_hash,
                now,
                created_by,
            ),
        )
    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            raise UserAlreadyExistsError(
                "A user with that email or username already exists."
            ) from error

        raise

    user_id = cursor.lastrowid

    row = connection.execute(
        """
        SELECT
            id,
            email,
            username,
            display_name,
            password_hash,
            is_active,
            created_at,
            created_by,
            last_login_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    return _row_to_user(row)

def create_user(
    *,
    email: str,
    username: str,
    display_name: str,
    password: str,
    created_by: int | None = None,
    role_name: str = STANDARD_USER,
) -> User:
    """Create a standalone AstroSphere user."""

    with get_connection() as connection:
        user = _create_user_with_connection(
            connection,
            email=email,
            username=username,
            display_name=display_name,
            password=password,
            created_by=created_by,
        )

        connection.commit()

    assign_role(
        user_id=user.id,
        role_name=role_name,
        assigned_by=created_by,
    )

    return get_user_by_id(user.id)

def get_all_users() -> list[User]:
    """Return all AstroSphere users ordered by creation time."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                email,
                username,
                display_name,
                password_hash,
                is_active,
                created_at,
                created_by,
                last_login_at
            FROM users
            ORDER BY created_at ASC, id ASC
            """
        ).fetchall()

    return [_row_to_user(row) for row in rows]

def create_super_administrator(
    *,
    email: str,
    username: str,
    display_name: str,
    password: str,
) -> User:
    from .rbac import (
        SUPER_ADMINISTRATOR,
        get_role,
        is_super_administrator,
    )

    email = email.strip().lower()
    username = username.strip().lower()
    display_name = display_name.strip()

    if not email:
        raise ValueError("Email is required.")

    if not username:
        raise ValueError("Username is required.")

    if not display_name:
        raise ValueError("Display name is required.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")

    if get_role(SUPER_ADMINISTRATOR) is None:
        raise RuntimeError(
            "Super Administrator role has not been initialized."
        )

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT u.id
            FROM users u
            INNER JOIN user_roles ur
                ON ur.user_id = u.id
            INNER JOIN roles r
                ON r.id = ur.role_id
            WHERE r.name = ?
            LIMIT 1
            """,
            (SUPER_ADMINISTRATOR,),
        ).fetchone()

        if existing is not None:
            raise PermissionError(
                "A Super Administrator already exists."
            )

        duplicate = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
               OR username = ?
            LIMIT 1
            """,
            (
                email,
                username,
            ),
        ).fetchone()

        if duplicate is not None:
            raise UserAlreadyExistsError(
                "A user with that email or username already exists."
            )

        now = datetime.now(timezone.utc).isoformat()

        password_hash = generate_password_hash(password)

        cursor = connection.execute(
            """
            INSERT INTO users (
                email,
                username,
                display_name,
                password_hash,
                is_active,
                created_at,
                created_by
            )
            VALUES (?, ?, ?, ?, 1, ?, NULL)
            """,
            (
                email,
                username,
                display_name,
                password_hash,
                now,
            ),
        )

        user_id = cursor.lastrowid

        role = connection.execute(
            """
            SELECT id
            FROM roles
            WHERE name = ?
            """,
            (SUPER_ADMINISTRATOR,),
        ).fetchone()

        connection.execute(
            """
            INSERT INTO user_roles (
                user_id,
                role_id,
                assigned_at,
                assigned_by
            )
            VALUES (?, ?, ?, NULL)
            """,
            (
                user_id,
                role["id"],
                now,
            ),
        )

        connection.execute(
            """
            INSERT INTO audit_log (
                actor_user_id,
                action,
                target_type,
                target_id,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                "super_administrator.created",
                "user",
                user_id,
                "Initial AstroSphere platform owner created.",
                now,
            ),
        )

        connection.commit()

    return get_user_by_id(user_id)

def get_user_by_id(user_id: int) -> User | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return _row_to_user(row)


def get_all_roles_with_permissions() -> list[dict]:
    """Return all platform and organization roles with their permissions."""

    with get_connection() as connection:
        roles = connection.execute(
            """
            SELECT
                r.id,
                r.name,
                r.description,
                r.is_system_role,
                r.created_at
            FROM roles r
            ORDER BY
                CASE
                    WHEN r.name = ? THEN 1
                    WHEN r.name = ? THEN 2
                    WHEN r.name = ? THEN 3
                    WHEN r.name = ? THEN 4
                    WHEN r.name = ? THEN 5
                    WHEN r.name = ? THEN 6
                    WHEN r.name = ? THEN 7
                    ELSE 8
                END,
                r.name
            """,
            (
                SUPER_ADMINISTRATOR,
                FULL_ADMINISTRATOR,
                STANDARD_USER,
                ORGANIZATION_ADMINISTRATOR,
                EDUCATOR,
                RESEARCHER,
                LEARNER,
            ),
        ).fetchall()

        result = []

        for role in roles:
            permissions = connection.execute(
                """
                SELECT
                    p.name,
                    p.description
                FROM role_permissions rp
                INNER JOIN permissions p
                    ON p.id = rp.permission_id
                WHERE rp.role_id = ?
                ORDER BY p.name
                """,
                (role["id"],),
            ).fetchall()

            result.append(
                {
                    "id": role["id"],
                    "name": role["name"],
                    "description": role["description"],
                    "is_system_role": bool(role["is_system_role"]),
                    "created_at": role["created_at"],
                    "permissions": [dict(permission) for permission in permissions],
                }
            )

        return result


def get_audit_log_entries(limit: int = 250) -> list[dict]:
    """Return recent platform audit events."""

    limit = max(1, min(int(limit), 1000))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                a.id,
                a.actor_user_id,
                a.action,
                a.target_type,
                a.target_id,
                a.details,
                a.created_at,
                u.username AS actor_username,
                u.display_name AS actor_display_name
            FROM audit_log a
            LEFT JOIN users u
                ON u.id = a.actor_user_id
            ORDER BY a.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]

def get_user_platform_roles(user_id: int) -> list[str]:
    """Return platform role names assigned to a user."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT r.name
            FROM user_roles ur
            INNER JOIN roles r
                ON r.id = ur.role_id
            WHERE ur.user_id = ?
            ORDER BY r.name
            """,
            (user_id,),
        ).fetchall()

    return [row["name"] for row in rows]


def get_primary_platform_role(user_id: int) -> str | None:
    """Return the user's primary platform role."""
    roles = get_user_platform_roles(user_id)

    if SUPER_ADMINISTRATOR in roles:
        return SUPER_ADMINISTRATOR

    if FULL_ADMINISTRATOR in roles:
        return FULL_ADMINISTRATOR

    if STANDARD_USER in roles:
        return STANDARD_USER

    return roles[0] if roles else None


def _write_audit_log(
    connection,
    *,
    actor_user_id: int | None,
    action: str,
    target_type: str,
    target_id: int | None,
    details: str,
) -> None:
    """Write an administrative audit event."""
    connection.execute(
        """
        INSERT INTO audit_log (
            actor_user_id,
            action,
            target_type,
            target_id,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            actor_user_id,
            action,
            target_type,
            target_id,
            details,
            utc_now(),
        ),
    )


def _validate_user_management_target(
    *,
    actor_user_id: int,
    target_user_id: int,
    allow_self: bool = True,
) -> User:
    """Validate that an administrator may manage the target user."""
    actor = get_user_by_id(actor_user_id)
    target = get_user_by_id(target_user_id)

    if actor is None:
        raise PermissionError("Administrator account was not found.")

    if target is None:
        raise ValueError("User not found.")

    actor_role = get_primary_platform_role(actor_user_id)
    target_role = get_primary_platform_role(target_user_id)

    if not allow_self and actor_user_id == target_user_id:
        raise PermissionError(
            "You cannot perform this action on your own account."
        )

    if actor_role == SUPER_ADMINISTRATOR:
        return target

    if actor_role != FULL_ADMINISTRATOR:
        raise PermissionError(
            "You do not have permission to manage platform users."
        )

    if target_role != STANDARD_USER:
        raise PermissionError(
            "Full Administrators may only manage Standard Users."
        )

    return target


def update_user(
    *,
    actor_user_id: int,
    target_user_id: int,
    email: str,
    username: str,
    display_name: str,
) -> User:
    """Update a platform user's basic profile information."""
    target = _validate_user_management_target(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
    )

    email = email.strip().lower()
    username = username.strip().lower()
    display_name = display_name.strip()

    if not email or not username or not display_name:
        raise ValueError(
            "Email, username, and display name are required."
        )

    with get_connection() as connection:
        duplicate = connection.execute(
            """
            SELECT id
            FROM users
            WHERE (email = ? OR username = ?)
              AND id != ?
            LIMIT 1
            """,
            (
                email,
                username,
                target_user_id,
            ),
        ).fetchone()

        if duplicate is not None:
            raise UserAlreadyExistsError(
                "A user with that email or username already exists."
            )

        connection.execute(
            """
            UPDATE users
            SET email = ?,
                username = ?,
                display_name = ?
            WHERE id = ?
            """,
            (
                email,
                username,
                display_name,
                target_user_id,
            ),
        )

        _write_audit_log(
            connection,
            actor_user_id=actor_user_id,
            action="user.updated",
            target_type="user",
            target_id=target_user_id,
            details=(
                f"Updated user profile for '{target.username}'."
            ),
        )

        connection.commit()

    return get_user_by_id(target_user_id)


def set_user_active(
    *,
    actor_user_id: int,
    target_user_id: int,
    is_active: bool,
) -> User:
    """Enable or disable a platform user."""
    target = _validate_user_management_target(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        allow_self=False,
    )

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET is_active = ?
            WHERE id = ?
            """,
            (
                1 if is_active else 0,
                target_user_id,
            ),
        )

        action = (
            "user.activated"
            if is_active
            else "user.deactivated"
        )

        state = "activated" if is_active else "deactivated"

        _write_audit_log(
            connection,
            actor_user_id=actor_user_id,
            action=action,
            target_type="user",
            target_id=target_user_id,
            details=f"User '{target.username}' was {state}.",
        )

        connection.commit()

    return get_user_by_id(target_user_id)


def delete_user(
    *,
    actor_user_id: int,
    target_user_id: int,
) -> None:
    """Permanently delete a platform user."""
    target = _validate_user_management_target(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        allow_self=False,
    )

    with get_connection() as connection:
        _write_audit_log(
            connection,
            actor_user_id=actor_user_id,
            action="user.deleted",
            target_type="user",
            target_id=target_user_id,
            details=f"User '{target.username}' was permanently deleted.",
        )

        connection.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """,
            (target_user_id,),
        )

        connection.commit()

def get_user_by_login(identifier: str) -> User | None:
    identifier = identifier.strip().lower()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
               OR username = ?
            LIMIT 1
            """,
            (
                identifier,
                identifier,
            ),
        ).fetchone()

    if row is None:
        return None

    return _row_to_user(row)


def create_password_reset_token(
    user_id: int,
) -> tuple[str, datetime]:
    from .security import (
        generate_secure_token,
        hash_token,
        password_reset_expiry,
    )

    token = generate_secure_token()
    token_hash = hash_token(token)
    expires_at = password_reset_expiry()
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = ?
            WHERE user_id = ?
              AND used_at IS NULL
            """,
            (
                now,
                user_id,
            ),
        )

        connection.execute(
            """
            INSERT INTO password_reset_tokens (
                user_id,
                token_hash,
                expires_at,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                token_hash,
                expires_at.isoformat(),
                now,
            ),
        )

        connection.commit()

    return token, expires_at


def get_user_for_password_reset(
    identifier: str,
) -> User | None:
    return get_user_by_login(identifier)


def reset_password(
    *,
    token: str,
    new_password: str,
) -> User:
    from .security import hash_token

    if len(new_password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    token_hash = hash_token(token)
    now = datetime.now(timezone.utc)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                pr.id,
                pr.user_id,
                pr.expires_at,
                pr.used_at
            FROM password_reset_tokens pr
            WHERE pr.token_hash = ?
            LIMIT 1
            """,
            (token_hash,),
        ).fetchone()

        if row is None:
            raise ValueError(
                "Invalid or expired password reset link."
            )

        if row["used_at"] is not None:
            raise ValueError(
                "Invalid or expired password reset link."
            )

        expires_at = datetime.fromisoformat(
            row["expires_at"]
        )

        if expires_at <= now:
            raise ValueError(
                "Invalid or expired password reset link."
            )

        password_hash = generate_password_hash(
            new_password
        )

        connection.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
            """,
            (
                password_hash,
                row["user_id"],
            ),
        )

        connection.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = ?
            WHERE id = ?
            """,
            (
                now.isoformat(),
                row["id"],
            ),
        )

        connection.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = ?
            WHERE user_id = ?
              AND used_at IS NULL
            """,
            (
                now.isoformat(),
                row["user_id"],
            ),
        )

        connection.commit()

    user = get_user_by_id(row["user_id"])

    if user is None:
        raise ValueError(
            "Unable to locate the user account."
        )

    return user


def change_password(
    *,
    user_id: int,
    current_password: str,
    new_password: str,
) -> User:
    if len(new_password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    user = get_user_by_id(user_id)

    if user is None:
        raise ValueError(
            "User account not found."
        )

    if not check_password_hash(
        user.password_hash,
        current_password,
    ):
        raise InvalidCredentialsError(
            "Current password is incorrect."
        )

    if current_password == new_password:
        raise ValueError(
            "New password must be different from the current password."
        )

    password_hash = generate_password_hash(
        new_password
    )

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
            """,
            (
                password_hash,
                user_id,
            ),
        )

        connection.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = ?
            WHERE user_id = ?
              AND used_at IS NULL
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                user_id,
            ),
        )

        connection.commit()

    return get_user_by_id(user_id)

def begin_mfa_enrollment(
    *,
    user_id: int,
) -> dict:
    user = get_user_by_id(user_id)

    if user is None:
        raise ValueError(
            "User account not found."
        )

    secret = generate_mfa_secret()
    encrypted_secret = encrypt_mfa_secret(secret)
    now = utc_now().isoformat()

    provisioning_uri = build_totp_uri(
        secret=secret,
        username=user.username,
        issuer="AstroSphere",
    )

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM mfa_recovery_codes
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.execute(
            """
            INSERT INTO user_mfa (
                user_id,
                method,
                secret_encrypted,
                is_enabled,
                created_at,
                last_verified_at
            )
            VALUES (?, ?, ?, 0, ?, NULL)
            ON CONFLICT(user_id)
            DO UPDATE SET
                method = excluded.method,
                secret_encrypted = excluded.secret_encrypted,
                is_enabled = 0,
                created_at = excluded.created_at,
                last_verified_at = NULL
            """,
            (
                user_id,
                "totp",
                encrypted_secret,
                now,
            ),
        )

        connection.commit()

    return {
        "user_id": user_id,
        "method": "totp",
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "is_enabled": False,
    }


def confirm_mfa_enrollment(
    *,
    user_id: int,
    code: str,
) -> list[str]:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                secret_encrypted,
                is_enabled
            FROM user_mfa
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            raise ValueError(
                "MFA enrollment has not been started."
            )

        secret = decrypt_mfa_secret(
            row["secret_encrypted"]
        )

        if not verify_totp_code(
            secret,
            code,
        ):
            raise ValueError(
                "Invalid MFA verification code."
            )

        now = utc_now().isoformat()

        connection.execute(
            """
            UPDATE user_mfa
            SET is_enabled = 1,
                last_verified_at = ?
            WHERE user_id = ?
            """,
            (
                now,
                user_id,
            ),
        )

        connection.execute(
            """
            DELETE FROM mfa_recovery_codes
            WHERE user_id = ?
            """,
            (user_id,),
        )

        recovery_codes = generate_recovery_codes()

        for recovery_code in recovery_codes:
            connection.execute(
                """
                INSERT INTO mfa_recovery_codes (
                    user_id,
                    code_hash,
                    used_at,
                    created_at
                )
                VALUES (?, ?, NULL, ?)
                """,
                (
                    user_id,
                    hash_recovery_code(recovery_code),
                    now,
                ),
            )

        connection.commit()

    return recovery_codes


def get_mfa_status(
    *,
    user_id: int,
) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                method,
                is_enabled,
                created_at,
                last_verified_at
            FROM user_mfa
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        recovery_row = connection.execute(
            """
            SELECT COUNT(*) AS remaining
            FROM mfa_recovery_codes
            WHERE user_id = ?
              AND used_at IS NULL
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return {
            "configured": False,
            "enabled": False,
            "method": None,
            "created_at": None,
            "last_verified_at": None,
            "recovery_codes_remaining": 0,
        }

    return {
        "configured": True,
        "enabled": bool(row["is_enabled"]),
        "method": row["method"],
        "created_at": row["created_at"],
        "last_verified_at": row["last_verified_at"],
        "recovery_codes_remaining": recovery_row["remaining"],
    }


def disable_mfa(
    *,
    user_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM mfa_recovery_codes
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.execute(
            """
            DELETE FROM user_mfa
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.commit()


def verify_mfa_code(
    *,
    user_id: int,
    code: str,
) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                secret_encrypted,
                is_enabled
            FROM user_mfa
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if row is None or not bool(row["is_enabled"]):
        return False

    secret = decrypt_mfa_secret(
        row["secret_encrypted"]
    )

    verified = verify_totp_code(
        secret,
        code,
    )

    if not verified:
        return False

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE user_mfa
            SET last_verified_at = ?
            WHERE user_id = ?
            """,
            (
                utc_now().isoformat(),
                user_id,
            ),
        )

        connection.commit()

    return True


def verify_mfa_recovery_code(
    *,
    user_id: int,
    code: str,
) -> bool:
    code_hash = hash_recovery_code(code)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id
            FROM mfa_recovery_codes
            WHERE user_id = ?
              AND code_hash = ?
              AND used_at IS NULL
            LIMIT 1
            """,
            (
                user_id,
                code_hash,
            ),
        ).fetchone()

        if row is None:
            return False

        connection.execute(
            """
            UPDATE mfa_recovery_codes
            SET used_at = ?
            WHERE id = ?
            """,
            (
                utc_now().isoformat(),
                row["id"],
            ),
        )

        connection.commit()

    return True

def authenticate_user(
    *,
    identifier: str,
    password: str,
) -> User:
    user = get_user_by_login(identifier)

    if user is None:
        raise InvalidCredentialsError(
            "Invalid email/username or password."
        )

    if not user.is_active:
        raise InvalidCredentialsError(
            "This account is inactive."
        )

    if not check_password_hash(
        user.password_hash,
        password,
    ):
        raise InvalidCredentialsError(
            "Invalid email/username or password."
        )

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE users
            SET last_login_at = ?
            WHERE id = ?
            """,
            (
                now,
                user.id,
            ),
        )

        connection.commit()

    return get_user_by_id(user.id)
