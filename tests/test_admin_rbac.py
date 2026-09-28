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


def test_super_admin_can_manage_all_platform_roles(auth_environment):
    service = auth_environment["service"]

    super_admin = _create_super_admin(service)
    full_admin = _create_full_admin(service)
    standard_user = _create_standard_user(service)

    assert service.get_primary_platform_role(
        super_admin.id
    ) == "super_administrator"

    assert service.get_primary_platform_role(
        full_admin.id
    ) == "full_administrator"

    assert service.get_primary_platform_role(
        standard_user.id
    ) == "standard_user"


def test_full_admin_can_manage_standard_user(auth_environment):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    standard_user = _create_standard_user(service)

    updated = service.update_user(
        actor_user_id=full_admin.id,
        target_user_id=standard_user.id,
        display_name="Updated Standard User",
        email="updated-standard@astro-test.local",
        username="updated_standard",
    )

    assert updated.display_name == "Updated Standard User"
    assert updated.email == "updated-standard@astro-test.local"
    assert updated.username == "updated_standard"


def test_full_admin_can_deactivate_and_activate_standard_user(
    auth_environment,
):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    standard_user = _create_standard_user(service)

    deactivated = service.set_user_active(
        actor_user_id=full_admin.id,
        target_user_id=standard_user.id,
        is_active=False,
    )

    assert deactivated.is_active is False

    activated = service.set_user_active(
        actor_user_id=full_admin.id,
        target_user_id=standard_user.id,
        is_active=True,
    )

    assert activated.is_active is True


def test_full_admin_cannot_modify_full_admin(auth_environment):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    target_full_admin = service.create_user(
        email="another-fulladmin@astro-test.local",
        username="anotherfulladmin",
        display_name="Another Full Administrator",
        password="TestPassword123!",
    )

    service.assign_role(
        target_full_admin.id,
        "full_administrator",
    )

    with pytest.raises(PermissionError):
        service.update_user(
            actor_user_id=full_admin.id,
            target_user_id=target_full_admin.id,
            email="another-fulladmin@astro-test.local",
            username="anotherfulladmin",
            display_name="Attempted Privilege Escalation",
        )


def test_full_admin_cannot_modify_super_admin(auth_environment):
    service = auth_environment["service"]

    super_admin = _create_super_admin(service)
    full_admin = _create_full_admin(service)

    with pytest.raises(PermissionError):
        service.update_user(
            actor_user_id=full_admin.id,
            target_user_id=super_admin.id,
            email="superadmin@astro-test.local",
            username="superadmin",
            display_name="Attempted Super Admin Modification",
        )


def test_full_admin_cannot_deactivate_full_admin(auth_environment):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    target_full_admin = service.create_user(
        email="target-fulladmin@astro-test.local",
        username="targetfulladmin",
        display_name="Target Full Administrator",
        password="TestPassword123!",
    )

    service.assign_role(
        target_full_admin.id,
        "full_administrator",
    )

    with pytest.raises(PermissionError):
        service.set_user_active(
            actor_user_id=full_admin.id,
            target_user_id=target_full_admin.id,
            is_active=False,
        )


def test_full_admin_cannot_deactivate_super_admin(auth_environment):
    service = auth_environment["service"]

    super_admin = _create_super_admin(service)
    full_admin = _create_full_admin(service)

    with pytest.raises(PermissionError):
        service.set_user_active(
            actor_user_id=full_admin.id,
            target_user_id=super_admin.id,
            is_active=False,
        )


def test_full_admin_cannot_delete_full_admin(auth_environment):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)
    target_full_admin = service.create_user(
        email="delete-target@astro-test.local",
        username="deletetarget",
        display_name="Delete Target Full Administrator",
        password="TestPassword123!",
    )

    service.assign_role(
        target_full_admin.id,
        "full_administrator",
    )

    with pytest.raises(PermissionError):
        service.delete_user(
            actor_user_id=full_admin.id,
            target_user_id=target_full_admin.id,
        )

    assert service.get_user_by_id(target_full_admin.id) is not None


def test_full_admin_cannot_delete_super_admin(auth_environment):
    service = auth_environment["service"]

    super_admin = _create_super_admin(service)
    full_admin = _create_full_admin(service)

    with pytest.raises(PermissionError):
        service.delete_user(
            actor_user_id=full_admin.id,
            target_user_id=super_admin.id,
        )

    assert service.get_user_by_id(super_admin.id) is not None


def test_admin_cannot_deactivate_themselves(auth_environment):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)

    with pytest.raises(PermissionError):
        service.set_user_active(
            actor_user_id=full_admin.id,
            target_user_id=full_admin.id,
            is_active=False,
        )

    assert service.get_user_by_id(full_admin.id).is_active is True


def test_admin_cannot_delete_themselves(auth_environment):
    service = auth_environment["service"]

    full_admin = _create_full_admin(service)

    with pytest.raises(PermissionError):
        service.delete_user(
            actor_user_id=full_admin.id,
            target_user_id=full_admin.id,
        )

    assert service.get_user_by_id(full_admin.id) is not None
