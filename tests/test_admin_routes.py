import importlib

import pytest


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
def client(auth_environment, monkeypatch):
    from web import app as app_module

    importlib.reload(app_module)

    app = app_module.app
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    return app.test_client()


def _create_super_admin(service):
    return service.create_super_administrator(
        email="superadmin@astro-test.local",
        username="superadmin",
        display_name="Test Super Administrator",
        password="TestPassword123!",
    )


def _create_full_admin(service):
    user = service.create_user(
        email="fulladmin@astro-test.local",
        username="fulladmin",
        display_name="Test Full Administrator",
        password="TestPassword123!",
    )

    service.assign_role(
        user.id,
        "full_administrator",
    )

    return service.get_user_by_id(user.id)


def _create_standard_user(service):
    return service.create_user(
        email="standard@astro-test.local",
        username="standard",
        display_name="Test Standard User",
        password="TestPassword123!",
    )


def _login(client, user):
    with client.session_transaction() as session:
        session["user_id"] = user.id


@pytest.mark.parametrize(
    "path",
    [
        "/admin",
        "/admin/organizations",
        "/admin/users",
        "/admin/roles",
        "/admin/audit-log",
    ],
)
def test_super_admin_can_access_platform_administration(
    auth_environment,
    client,
    path,
):
    service = auth_environment["service"]

    super_admin = _create_super_admin(service)

    _login(client, super_admin)

    response = client.get(path)

    assert response.status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/user-management",
    ],
)
def test_full_admin_can_access_user_management(
    auth_environment,
    client,
    path,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)

    _login(client, full_admin)

    response = client.get(path)

    assert response.status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/admin",
        "/admin/organizations",
        "/admin/users",
        "/admin/roles",
        "/admin/audit-log",
    ],
)
def test_full_admin_cannot_access_platform_administration(
    auth_environment,
    client,
    path,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)

    _login(client, full_admin)

    response = client.get(path)

    assert response.status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "/admin",
        "/admin/organizations",
        "/admin/users",
        "/admin/roles",
        "/admin/audit-log",
        "/user-management",
    ],
)
def test_standard_user_cannot_access_admin_routes(
    auth_environment,
    client,
    path,
):
    service = auth_environment["service"]

    standard_user = _create_standard_user(service)

    _login(client, standard_user)

    response = client.get(path)

    assert response.status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "/admin",
        "/admin/organizations",
        "/admin/users",
        "/admin/roles",
        "/admin/audit-log",
        "/user-management",
    ],
)
def test_unauthenticated_user_is_redirected_to_login(
    client,
    path,
):
    response = client.get(path)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_full_admin_can_create_standard_user(
    auth_environment,
    client,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)

    _login(client, full_admin)

    response = client.post(
        "/user-management/create",
        data={
            "email": "created@astro-test.local",
            "username": "created_standard",
            "display_name": "Created Standard User",
            "password": "TestPassword123!",
        },
        follow_redirects=False,
    )

    assert response.status_code in {302, 303}

    created = service.get_user_by_login("created_standard")

    assert created is not None
    assert service.get_primary_platform_role(created.id) == "standard_user"


def test_full_admin_cannot_create_elevated_user_through_management_route(
    auth_environment,
    client,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)

    _login(client, full_admin)

    response = client.post(
        "/user-management/create",
        data={
            "email": "attempted-admin@astro-test.local",
            "username": "attempted_admin",
            "display_name": "Attempted Administrator",
            "password": "TestPassword123!",
            "role": "full_administrator",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    created = service.get_user_by_login("attempted_admin")
    assert created is not None
    assert service.get_primary_platform_role(created.id) == "standard_user"


def test_full_admin_cannot_directly_edit_elevated_user(
    auth_environment,
    client,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    target_full_admin = service.create_user(
        email="target-admin@astro-test.local",
        username="target_admin",
        display_name="Target Full Administrator",
        password="TestPassword123!",
    )

    service.assign_role(
        target_full_admin.id,
        "full_administrator",
    )

    _login(client, full_admin)

    response = client.post(
        f"/user-management/{target_full_admin.id}/edit",
        data={
            "email": "changed@astro-test.local",
            "username": "changed_admin",
            "display_name": "Attempted Change",
        },
        follow_redirects=False,
    )

    assert response.status_code == 403

    unchanged = service.get_user_by_id(target_full_admin.id)

    assert unchanged.email == "target-admin@astro-test.local"
    assert unchanged.username == "target_admin"
    assert unchanged.display_name == "Target Full Administrator"


def test_full_admin_cannot_directly_delete_elevated_user(
    auth_environment,
    client,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    target_full_admin = service.create_user(
        email="delete-admin@astro-test.local",
        username="delete_admin",
        display_name="Delete Target Administrator",
        password="TestPassword123!",
    )

    service.assign_role(
        target_full_admin.id,
        "full_administrator",
    )

    _login(client, full_admin)

    response = client.post(
        f"/user-management/{target_full_admin.id}/delete",
        follow_redirects=False,
    )

    assert response.status_code == 403

    assert service.get_user_by_id(target_full_admin.id) is not None
