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
        email="admin@astro-test.local",
        username="admin",
        display_name="Test Super Administrator",
        password="TestPassword123!",
    )


def _create_standard_user(service):
    return service.create_user(
        email="learner@astro-test.local",
        username="learner",
        display_name="Test Learner",
        password="TestPassword123!",
    )


def _create_organization(organization, created_by):
    return organization.create_organization(
        name="AstroSphere Test School",
        slug="astrosphere-test-school",
        organization_type="SCHOOL",
        created_by=created_by,
    )


def test_auth_database_is_isolated(auth_environment):
    database = auth_environment["database"]
    service = auth_environment["service"]

    users = service.get_all_users()

    assert users == []

    with database.get_connection() as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS count FROM users"
        ).fetchone()

    assert row["count"] == 0


def test_super_administrator_has_unrestricted_organization_access(
    auth_environment,
):
    rbac = auth_environment["rbac"]
    service = auth_environment["service"]
    organization = auth_environment["organization"]

    admin = _create_super_admin(service)
    school = _create_organization(organization, admin.id)

    assert rbac.is_super_administrator(admin.id)

    assert rbac.organization_user_has_permission(
        admin.id,
        school.id,
        "users.view",
    )

    assert rbac.organization_user_has_permission(
        admin.id,
        school.id,
        "users.create",
    )

    permissions = rbac.get_organization_user_permissions(
        admin.id,
        school.id,
    )

    assert "users.view" in permissions
    assert "users.create" in permissions


def test_learner_does_not_have_organization_user_administration(
    auth_environment,
):
    rbac = auth_environment["rbac"]
    service = auth_environment["service"]
    organization = auth_environment["organization"]

    admin = _create_super_admin(service)
    learner = _create_standard_user(service)
    school = _create_organization(organization, admin.id)

    membership = organization.add_organization_member(
        organization_id=school.id,
        user_id=learner.id,
    )

    learner_role = rbac.get_role("learner")

    assert learner_role is not None

    organization.assign_organization_role(
        membership_id=membership.id,
        role_id=learner_role["id"],
        assigned_by=admin.id,
    )

    assert not rbac.organization_user_has_permission(
        learner.id,
        school.id,
        "users.view",
    )

    assert not rbac.organization_user_has_permission(
        learner.id,
        school.id,
        "users.create",
    )


@pytest.mark.parametrize(
    "organization_role",
    [
        "learner",
        "educator",
        "researcher",
    ],
)
def test_create_organization_user_assigns_allowed_role(
    auth_environment,
    organization_role,
):
    service = auth_environment["service"]
    organization = auth_environment["organization"]

    admin = _create_super_admin(service)
    school = _create_organization(organization, admin.id)

    created = organization.create_organization_user(
        organization_id=school.id,
        created_by=admin.id,
        email=f"{organization_role}@astro-test.local",
        username=f"{organization_role}_user",
        display_name=f"Test {organization_role.title()}",
        password="TestPassword123!",
        organization_role=organization_role,
    )

    assert created.id is not None

    membership = organization.get_membership(
        organization_id=school.id,
        user_id=created.id,
    )

    assert membership is not None
    assert membership.status == "active"

    roles = organization.get_membership_roles(membership.id)

    assert [role["name"] for role in roles] == [organization_role]


def test_create_organization_user_rejects_organization_administrator(
    auth_environment,
):
    service = auth_environment["service"]
    organization = auth_environment["organization"]

    admin = _create_super_admin(service)
    school = _create_organization(organization, admin.id)

    with pytest.raises(organization.OrganizationUserCreationError):
        organization.create_organization_user(
            organization_id=school.id,
            created_by=admin.id,
            email="forbidden@astro-test.local",
            username="forbidden",
            display_name="Forbidden User",
            password="TestPassword123!",
            organization_role="organization_administrator",
        )

    assert service.get_user_by_login("forbidden") is None


def test_organization_user_creation_is_atomic(
    auth_environment,
):
    service = auth_environment["service"]
    organization = auth_environment["organization"]
    database = auth_environment["database"]
    rbac = auth_environment["rbac"]

    admin = _create_super_admin(service)
    school = _create_organization(organization, admin.id)

    learner_role = rbac.get_role("learner")

    assert learner_role is not None

    now = organization._utc_now()

    with database.get_connection() as connection:
        user = service._create_user_with_connection(
            connection,
            email="rollback@astro-test.local",
            username="rollback",
            display_name="Rollback User",
            password="TestPassword123!",
            created_by=admin.id,
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
                school.id,
                user.id,
                now,
                now,
            ),
        )

        membership_id = cursor.lastrowid

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
                learner_role["id"],
                now,
                admin.id,
            ),
        )

        try:
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
                    learner_role["id"],
                    now,
                    admin.id,
                ),
            )
        except Exception:
            connection.rollback()

    assert service.get_user_by_login("rollback") is None

    with database.get_connection() as connection:
        membership = connection.execute(
            """
            SELECT id
            FROM organization_memberships
            WHERE organization_id = ?
              AND user_id = ?
            """,
            (school.id, user.id),
        ).fetchone()

    assert membership is None

def test_organization_boundary_prevents_cross_tenant_membership(
    auth_environment,
):
    rbac = auth_environment["rbac"]
    service = auth_environment["service"]
    organization = auth_environment["organization"]

    admin = _create_super_admin(service)

    school_one = _create_organization(
        organization,
        admin.id,
    )

    school_two = organization.create_organization(
        name="Second AstroSphere School",
        slug="second-astrosphere-school",
        organization_type="SCHOOL",
        created_by=admin.id,
    )

    user = organization.create_organization_user(
        organization_id=school_one.id,
        created_by=admin.id,
        email="tenant-user@astro-test.local",
        username="tenant_user",
        display_name="Tenant User",
        password="TestPassword123!",
        organization_role="learner",
    )

    assert organization.get_membership(
        organization_id=school_one.id,
        user_id=user.id,
    ) is not None

    assert organization.get_membership(
        organization_id=school_two.id,
        user_id=user.id,
    ) is None

    assert rbac.organization_user_has_permission(
        user.id,
        school_one.id,
        "astronomy.view",
    )

    assert not rbac.organization_user_has_permission(
        user.id,
        school_two.id,
        "astronomy.view",
    )
