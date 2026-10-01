import importlib
import time

import pytest
from flask import session


@pytest.fixture()
def auth_environment(tmp_path, monkeypatch):
    database_path = tmp_path / "users.db"

    monkeypatch.setenv(
        "ASTROSPHERE_USERS_DATABASE",
        str(database_path),
    )

    import astrosphere.auth.database as database
    import astrosphere.auth.rbac as rbac

    importlib.reload(database)
    importlib.reload(rbac)

    database.initialize_database()
    rbac.initialize_rbac()

    import astrosphere.auth.organization as organization
    import astrosphere.auth.service as service

    importlib.reload(organization)
    importlib.reload(service)

    return {
        "database": database,
        "rbac": rbac,
        "organization": organization,
        "service": service,
    }


@pytest.fixture()
def client(auth_environment):
    from web import app as app_module

    importlib.reload(app_module)

    app = app_module.app
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    return app.test_client()


def _create_user(service):
    return service.create_user(
        email="timeout@astro-test.local",
        username="timeout_user",
        display_name="Session Timeout User",
        password="TestPassword123!",
    )


def test_login_creates_last_activity_timestamp(
    auth_environment,
    client,
):
    from web.auth import SESSION_LAST_ACTIVITY, login_user

    user = _create_user(auth_environment["service"])

    with client.application.test_request_context():
        login_user(user)

        assert session["user_id"] == user.id
        assert SESSION_LAST_ACTIVITY in session
        assert isinstance(session[SESSION_LAST_ACTIVITY], float)


def test_active_session_is_valid(
    auth_environment,
    client,
):
    from web.auth import (
        SESSION_LAST_ACTIVITY,
        get_current_user,
    )

    user = _create_user(auth_environment["service"])

    with client.application.test_request_context():
        session["user_id"] = user.id
        session[SESSION_LAST_ACTIVITY] = time.time()

        assert get_current_user() is not None
        assert get_current_user().id == user.id


def test_expired_session_is_cleared(
    auth_environment,
    client,
    monkeypatch,
):
    from web.auth import (
        SESSION_LAST_ACTIVITY,
        SESSION_USER_ID,
        get_current_user,
    )

    user = _create_user(auth_environment["service"])

    monkeypatch.setenv(
        "ASTROSPHERE_SESSION_IDLE_TIMEOUT_SECONDS",
        "60",
    )

    with client.application.test_request_context():
        session[SESSION_USER_ID] = user.id
        session[SESSION_LAST_ACTIVITY] = time.time() - 61

        assert get_current_user() is None
        assert SESSION_USER_ID not in session
        assert SESSION_LAST_ACTIVITY not in session


def test_activity_refreshes_session_timeout(
    auth_environment,
    client,
    monkeypatch,
):
    from web.auth import (
        SESSION_LAST_ACTIVITY,
        SESSION_USER_ID,
        get_current_user,
    )

    user = _create_user(auth_environment["service"])

    monkeypatch.setenv(
        "ASTROSPHERE_SESSION_IDLE_TIMEOUT_SECONDS",
        "60",
    )

    with client.application.test_request_context():
        session[SESSION_USER_ID] = user.id
        session[SESSION_LAST_ACTIVITY] = time.time()

        old_activity = session[SESSION_LAST_ACTIVITY]

        time.sleep(0.01)

        assert get_current_user() is not None

        new_activity = session[SESSION_LAST_ACTIVITY]

        assert new_activity > old_activity


def test_logout_clears_authenticated_session(
    auth_environment,
    client,
):
    from web.auth import (
        SESSION_LAST_ACTIVITY,
        SESSION_USER_ID,
        logout_user,
    )

    user = _create_user(auth_environment["service"])

    with client.application.test_request_context():
        session[SESSION_USER_ID] = user.id
        session[SESSION_LAST_ACTIVITY] = time.time()

        logout_user()

        assert SESSION_USER_ID not in session
        assert SESSION_LAST_ACTIVITY not in session


def test_completed_mfa_login_creates_last_activity_timestamp(
    auth_environment,
    client,
):
    from web.auth import (
        SESSION_LAST_ACTIVITY,
        SESSION_MFA_PENDING_USER_ID,
        complete_mfa_login,
    )

    user = _create_user(auth_environment["service"])

    with client.application.test_request_context():
        session[SESSION_MFA_PENDING_USER_ID] = user.id

        complete_mfa_login(user)

        assert session["user_id"] == user.id
        assert SESSION_LAST_ACTIVITY in session
        assert isinstance(session[SESSION_LAST_ACTIVITY], float)



def test_expired_session_redirects_protected_route(
    auth_environment,
    client,
    monkeypatch,
):
    from web.auth import SESSION_LAST_ACTIVITY, SESSION_USER_ID

    user = _create_user(auth_environment["service"])

    monkeypatch.setenv(
        "ASTROSPHERE_SESSION_IDLE_TIMEOUT_SECONDS",
        "60",
    )

    with client.session_transaction() as session:
        session[SESSION_USER_ID] = user.id
        session[SESSION_LAST_ACTIVITY] = time.time() - 61

    response = client.get("/app")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

    with client.session_transaction() as session:
        assert SESSION_USER_ID not in session
        assert SESSION_LAST_ACTIVITY not in session
