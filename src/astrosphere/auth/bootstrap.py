from getpass import getpass

from astrosphere.auth.rbac import (
    SUPER_ADMINISTRATOR,
    initialize_rbac,
)
from astrosphere.auth.database import initialize_database
from astrosphere.auth.service import (
    UserAlreadyExistsError,
    create_super_administrator,
)


def _prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()

        if value:
            return value

        print(f"{label} is required.")


def _prompt_password() -> str:
    while True:
        password = getpass("Password: ")

        if not password:
            print("Password is required.")
            continue

        confirmation = getpass("Confirm password: ")

        if password != confirmation:
            print("Passwords do not match.")
            continue

        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            continue

        return password


def main() -> None:
    initialize_database()
    initialize_rbac()

    print()
    print("=" * 64)
    print("AstroSphere Super Administrator Bootstrap")
    print("=" * 64)
    print()
    print(
        "This process creates the initial Super Administrator account."
    )
    print(
        "It should only be used during initial platform setup."
    )
    print()

    email = _prompt_required("Email")
    username = _prompt_required("Username")
    display_name = _prompt_required("Display name")
    password = _prompt_password()

    print()
    print("Account details:")
    print(f"  Display name: {display_name}")
    print(f"  Username:     {username}")
    print(f"  Email:        {email}")
    print(f"  Role:         {SUPER_ADMINISTRATOR}")
    print()

    confirmation = input(
        "Create this Super Administrator account? [Y/N]: "
    ).strip().lower()

    if confirmation not in {"y", "yes"}:
        print("Bootstrap cancelled.")
        return

    try:
        user = create_super_administrator(
            email=email,
            username=username,
            display_name=display_name,
            password=password,
        )
    except UserAlreadyExistsError as exc:
        print()
        print(f"Bootstrap failed: {exc}")
        return
    except ValueError as exc:
        print()
        print(f"Bootstrap failed: {exc}")
        return

    print()
    print("=" * 64)
    print("Super Administrator created successfully.")
    print("=" * 64)
    print()
    print(f"User ID:      {user.id}")
    print(f"Display name: {user.display_name}")
    print(f"Username:     {user.username}")
    print(f"Email:        {user.email}")
    print(f"Role:         {SUPER_ADMINISTRATOR}")
    print()
    print("You can now sign in through the AstroSphere login page.")
    print()


if __name__ == "__main__":
    main()
