from __future__ import annotations

import getpass

from astrosphere.auth.database import (
    get_connection,
    initialize_database,
)
from astrosphere.auth.rbac import (
    SUPER_ADMINISTRATOR,
    initialize_rbac,
)
from astrosphere.auth.service import (
    UserAlreadyExistsError,
    create_super_administrator,
)


def super_admin_exists() -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM user_roles ur
            INNER JOIN roles r
                ON r.id = ur.role_id
            WHERE r.name = ?
            LIMIT 1
            """,
            (SUPER_ADMINISTRATOR,),
        ).fetchone()

    return row is not None


def main() -> None:
    initialize_database()
    initialize_rbac()

    if super_admin_exists():
        raise SystemExit(
            "A Super Administrator already exists. "
            "Bootstrap has been refused."
        )

    print()
    print("==============================================")
    print(" AstroSphere Super Administrator Bootstrap")
    print("==============================================")
    print()

    print("Display name: ", end="", flush=True)
    display_name = input().strip()

    print("Username: ", end="", flush=True)
    username = input().strip()

    print("Email address: ", end="", flush=True)
    email = input().strip()

    print("Password: ", end="", flush=True)
    password = getpass.getpass("")

    print("Confirm password: ", end="", flush=True)
    confirm_password = getpass.getpass("")

    if password != confirm_password:
        raise SystemExit("Passwords do not match.")

    if len(password) < 8:
        raise SystemExit(
            "Password must be at least 8 characters."
        )

    try:
        user = create_super_administrator(
            email=email,
            username=username,
            display_name=display_name,
            password=password,
        )
    except UserAlreadyExistsError as error:
        raise SystemExit(str(error))
    except PermissionError as error:
        raise SystemExit(str(error))

    print()
    print("==============================================")
    print(" Super Administrator created successfully")
    print("==============================================")
    print()
    print(f"Username : {user.username}")
    print(f"Email    : {user.email}")
    print(f"Display  : {user.display_name}")
    print(f"User ID  : {user.id}")
    print()
    print("AstroSphere owner account is ready.")
    print()


if __name__ == "__main__":
    main()
