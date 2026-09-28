from __future__ import annotations

from functools import wraps
from urllib.parse import urlparse

from flask import (
    redirect,
    request,
    session,
    url_for,
)

from astrosphere.auth.models import User
from astrosphere.auth.organization import (
    get_organization,
    get_membership,
    get_user_memberships,
)
from astrosphere.auth.rbac import (
    get_organization_user_permissions,
    is_super_administrator,
    organization_user_has_permission,
    user_has_permission,
)
from astrosphere.auth.service import get_user_by_id


SESSION_USER_ID = "user_id"
SESSION_MFA_PENDING_USER_ID = "mfa_pending_user_id"
SESSION_MFA_NEXT_URL = "mfa_next_url"
SESSION_ORGANIZATION_ID = "organization_id"


def get_current_user() -> User | None:
    """Return the authenticated user for the current request."""
    user_id = session.get(SESSION_USER_ID)

    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        session.pop(SESSION_USER_ID, None)
        return None

    user = get_user_by_id(user_id)

    if user is None or not user.is_active:
        session.pop(SESSION_USER_ID, None)
        return None

    return user


def login_user(user: User) -> None:
    """Create an authenticated session for a user."""
    session.clear()
    session[SESSION_USER_ID] = user.id

    memberships = get_user_memberships(user.id)

    if len(memberships) == 1:
        session[SESSION_ORGANIZATION_ID] = memberships[0].organization_id


def get_current_organization_id() -> int | None:
    """Return the selected organization ID for the current session."""
    organization_id = session.get(SESSION_ORGANIZATION_ID)

    if organization_id is None:
        return None

    try:
        return int(organization_id)
    except (TypeError, ValueError):
        session.pop(SESSION_ORGANIZATION_ID, None)
        return None


def set_current_organization(organization_id: int) -> bool:
    """Select an active organization for the authenticated user."""
    user = get_current_user()

    if user is None:
        return False

    organization = get_organization(organization_id)

    if organization is None or not organization.is_active:
        return False

    if not is_super_administrator(user.id):
        membership = get_membership(
            organization_id=organization_id,
            user_id=user.id,
        )

        if membership is None or membership.status != "active":
            return False

    session[SESSION_ORGANIZATION_ID] = organization_id

    return True

def clear_current_organization() -> None:
    """Clear the current organization selection."""
    session.pop(SESSION_ORGANIZATION_ID, None)


def get_current_organization():
    """Return the active organization for the current session."""
    organization_id = get_current_organization_id()

    if organization_id is None:
        return None

    user = get_current_user()

    if user is None:
        clear_current_organization()
        return None

    organization = get_organization(organization_id)

    if organization is None or not organization.is_active:
        clear_current_organization()
        return None

    if is_super_administrator(user.id):
        return organization

    membership = get_membership(
        organization_id=organization_id,
        user_id=user.id,
    )

    if membership is None or membership.status != "active":
        clear_current_organization()
        return None

    return organization

def get_current_membership():
    """Return the current user's active organization membership."""
    organization = get_current_organization()

    if organization is None:
        return None

    user = get_current_user()

    if user is None:
        return None

    return get_membership(
        organization_id=organization.id,
        user_id=user.id,
    )


def get_current_organization_permissions() -> set[str]:
    """Return permissions for the current user in the selected organization."""
    user = get_current_user()
    organization = get_current_organization()

    if user is None or organization is None:
        return set()

    return get_organization_user_permissions(
        user.id,
        organization.id,
    )

def begin_mfa_login(
    user: User,
    next_url: str | None = None,
) -> None:
    """Store a user in the temporary MFA verification state."""
    session.clear()
    session[SESSION_MFA_PENDING_USER_ID] = user.id

    if is_safe_redirect_target(next_url):
        session[SESSION_MFA_NEXT_URL] = next_url


def get_mfa_pending_user() -> User | None:
    """Return the user awaiting MFA verification."""
    user_id = session.get(
        SESSION_MFA_PENDING_USER_ID
    )

    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        clear_mfa_pending()
        return None

    user = get_user_by_id(user_id)

    if user is None or not user.is_active:
        clear_mfa_pending()
        return None

    return user


def get_mfa_pending_next_url() -> str:
    """Return the safe redirect target saved before MFA."""
    target = session.get(
        SESSION_MFA_NEXT_URL
    )

    if is_safe_redirect_target(target):
        return target

    return url_for("index")


def complete_mfa_login(user: User) -> str:
    """Convert a successful MFA challenge into an authenticated session."""
    next_url = get_mfa_pending_next_url()

    session.clear()
    session[SESSION_USER_ID] = user.id

    return next_url


def clear_mfa_pending() -> None:
    """Clear any pending MFA authentication state."""
    session.pop(
        SESSION_MFA_PENDING_USER_ID,
        None,
    )
    session.pop(
        SESSION_MFA_NEXT_URL,
        None,
    )

def logout_user() -> None:
    """Destroy the current authenticated session."""
    session.clear()


def is_safe_redirect_target(target: str | None) -> bool:
    """Return True only for local application paths."""
    if not target:
        return False

    parsed = urlparse(target)

    return (
        not parsed.scheme
        and not parsed.netloc
        and target.startswith("/")
        and not target.startswith("//")
    )


def get_safe_next_url(target: str | None) -> str:
    """Return a safe local redirect target or the application home."""
    if is_safe_redirect_target(target):
        return target

    return url_for("index")


def login_required(view):
    """Require an authenticated AstroSphere user."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()

        if user is None:
            next_url = request.full_path.rstrip("?")

            return redirect(
                url_for(
                    "login",
                    next=next_url,
                )
            )

        return view(*args, **kwargs)

    return wrapped_view
def permission_required(permission_name: str):
    """Require authentication and a specific AstroSphere permission."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = get_current_user()

            if user is None:
                next_url = request.full_path.rstrip("?")

                return redirect(
                    url_for(
                        "login",
                        next=next_url,
                    )
                )

            if not user_has_permission(
                user.id,
                permission_name,
            ):
                from flask import abort

                abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorator




def organization_permission_required(permission_name: str):
    """Require authentication and a permission within the current organization."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = get_current_user()

            if user is None:
                next_url = request.full_path.rstrip("?")

                return redirect(
                    url_for(
                        "login",
                        next=next_url,
                    )
                )

            organization = get_current_organization()

            if organization is None:
                from flask import abort
                abort(403)

            if not organization_user_has_permission(
                user.id,
                organization.id,
                permission_name,
            ):
                from flask import abort
                abort(403)

            return view(*args, **kwargs)

        return wrapped_view

    return decorator
