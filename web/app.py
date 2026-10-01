import base64
import os
from io import BytesIO

from datetime import datetime, timezone

import qrcode

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)

from astrosphere.astronomy.orbital_analysis import (
    analyze_body_distance,
)

from astrosphere.astronomy.calculations import (
    calculate_distance_km,
    calculate_relative_velocity_km_s,
    get_current_time,
    load_solar_system,
)

from astrosphere.astronomy.planets import (
    PLANET_LOOKUP,
)

from astrosphere.astronomy.spacecraft import (
    SpacecraftNotFoundError,
    SpacecraftServiceError,
    track_spacecraft_by_norad,
)

from astrosphere.scientific.service import (
    get_scientific_data,
    get_ephemeris_data_source,
)

from astrosphere.scientific.context import (
    get_celestial_object_context,
)

from astrosphere.models.celestial_registry import (
    get_celestial_object,
)

from astrosphere.analysis_config import (
    AnalysisConfig,
)

from astrosphere.overview import (
    generate_solar_system_overview,
)

from astrosphere.config import (
    AppConfig,
)

from web.api import (
    api,
)

from astrosphere.navigation import (
    get_celestial_object_url,
)

from astrosphere.auth.database import (
    initialize_database,
)
from astrosphere.auth.organization import (
    OrganizationAlreadyExistsError,
    OrganizationNotFoundError,
    OrganizationUserCreationError,
    ORGANIZATION_TYPES,
    activate_organization,
    create_organization,
    create_organization_user,
    deactivate_organization,
    delete_organization,
    get_all_organizations,
    get_assignable_organization_roles,
    get_organization,
    get_organization_members,
    get_membership_roles,
    update_organization,
)

from astrosphere.auth.rbac import (
    FULL_ADMINISTRATOR,
    STANDARD_USER,
    SUPER_ADMINISTRATOR,
    get_organization_membership_roles,
    initialize_rbac,
    user_has_permission,
)

from astrosphere.auth.service import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    authenticate_user,
    begin_mfa_enrollment,
    confirm_mfa_enrollment,
    create_password_reset_token,
    create_user,
    delete_user,
    disable_mfa,
    get_all_users,
    get_primary_platform_role,
    get_user_platform_roles,
    get_all_roles_with_permissions,
    get_audit_log_entries,
    get_mfa_status,
    get_user_by_id,
    get_user_for_password_reset,
    reset_password,
    set_user_active,
    update_user,
    verify_mfa_code,
    verify_mfa_recovery_code,
)

from web.auth import (
    begin_mfa_login,
    clear_mfa_pending,
    complete_mfa_login,
    get_current_membership,
    get_current_organization,
    get_current_user,
    get_mfa_pending_next_url,
    get_mfa_pending_user,
    get_safe_next_url,
    login_required,
    login_user,
    logout_user,
    organization_permission_required,
)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "ASTROSPHERE_SECRET_KEY",
    "astrosphere-local-development-secret",
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "ASTROSPHERE_SECURE_COOKIES",
    "false",
).lower() == "true"

initialize_database()
initialize_rbac()


@app.template_global()
def celestial_url(object_id):
    return get_celestial_object_url(object_id)

@app.template_global()
def can_access_platform_administration(permission_name="users.view"):
    """Return True only for Super Administrators."""

    user = get_current_user()

    if user is None:
        return False

    return get_primary_platform_role(user.id) == SUPER_ADMINISTRATOR


@app.template_global()
def can_access_user_management():
    """Return True for Full Administrators and Super Administrators."""

    user = get_current_user()

    if user is None:
        return False

    role = get_primary_platform_role(user.id)

    return role in {
        SUPER_ADMINISTRATOR,
        FULL_ADMINISTRATOR,
    }


app.register_blueprint(api)


@app.route("/")
def landing():

    return render_template(
        "landing.html"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next", "")

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        next_url = request.form.get("next", next_url)

        try:
            user = authenticate_user(
                identifier=identifier,
                password=password,
            )

        except InvalidCredentialsError:
            return render_template(
                "login.html",
                error="Invalid email/username or password.",
                identifier=identifier,
                next_url=next_url,
            ), 401

        mfa_status = get_mfa_status(
            user_id=user.id,
        )

        if mfa_status["enabled"]:
            begin_mfa_login(
                user=user,
                next_url=next_url,
            )

            return redirect(
                url_for("mfa_challenge")
            )

        login_user(user)

        if next_url:
            return redirect(
                get_safe_next_url(next_url)
            )

        return redirect(
            url_for("profile")
        )

    return render_template(
        "login.html",
        error=None,
        identifier="",
        next_url=next_url,
    )


@app.route("/mfa", methods=["GET", "POST"])
def mfa_challenge():
    user = get_mfa_pending_user()

    if user is None:
        return redirect(
            url_for("login")
        )

    if request.method == "POST":
        code = request.form.get(
            "code",
            "",
        ).strip()

        method = request.form.get(
            "method",
            "totp",
        ).strip().lower()

        verified = False

        if method == "recovery":
            verified = verify_mfa_recovery_code(
                user_id=user.id,
                code=code,
            )
        else:
            verified = verify_mfa_code(
                user_id=user.id,
                code=code,
            )

        if not verified:
            return render_template(
                "mfa_challenge.html",
                error="The verification code is invalid or has already been used.",
                recovery_mode=(method == "recovery"),
            ), 401

        next_url = complete_mfa_login(user)

        return redirect(
            get_safe_next_url(next_url)
        )

    recovery_mode = (
        request.args.get("recovery", "").strip() == "1"
    )

    return render_template(
        "mfa_challenge.html",
        error=None,
        recovery_mode=recovery_mode,
    )

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()

        # Always return the same message so that the endpoint
        # does not reveal whether an account exists.
        message = (
            "If an account exists for that information, "
            "password-reset instructions have been prepared."
        )

        if identifier:
            user = get_user_for_password_reset(identifier)

            if user is not None and user.is_active:
                create_password_reset_token(user.id)

        return render_template(
            "forgot_password.html",
            message=message,
            identifier=identifier,
            error=None,
        )

    return render_template(
        "forgot_password.html",
        message=None,
        identifier="",
        error=None,
    )


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_route(token):
    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password != confirm_password:
            return render_template(
                "reset_password.html",
                token=token,
                error="The passwords do not match.",
                success=None,
            ), 400

        try:
            reset_password(
                token=token,
                new_password=new_password,
            )
        except ValueError as exc:
            return render_template(
                "reset_password.html",
                token=token,
                error=str(exc),
                success=None,
            ), 400

        return render_template(
            "reset_password.html",
            token=None,
            error=None,
            success=(
                "Your password has been reset successfully. "
                "You can now sign in with your new password."
            ),
        )

    return render_template(
        "reset_password.html",
        token=token,
        error=None,
        success=None,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    return redirect(url_for("login"))

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()

    return redirect(
        url_for("landing")
    )


def _mfa_qr_data_uri(provisioning_uri: str) -> str:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )

    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    image = qr.make_image()

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return f"data:image/png;base64,{encoded}"


def _get_profile_organization_context(user):
    """Build organization and role information for the profile page."""
    organization = get_current_organization()
    membership = get_current_membership()

    organization_roles = []

    if membership is not None:
        organization_roles = get_organization_membership_roles(
            user.id,
            organization.id,
        )

    return {
        "organization": organization,
        "membership": membership,
        "organization_roles": organization_roles,
    }


def _platform_admin_required():
    """Require the Super Administrator platform role."""

    user = get_current_user()

    if user is None:
        return redirect(url_for("login"))

    if get_primary_platform_role(user.id) != SUPER_ADMINISTRATOR:
        return render_template(
            "error.html",
            status_code=403,
            message="You do not have permission to access this administration area.",
        ), 403

    return None


def _user_management_required():
    """Require Full Administrator or Super Administrator."""

    user = get_current_user()

    if user is None:
        return redirect(url_for("login"))

    role = get_primary_platform_role(user.id)

    if role not in {
        SUPER_ADMINISTRATOR,
        FULL_ADMINISTRATOR,
    }:
        return render_template(
            "error.html",
            status_code=403,
            message="You do not have permission to access user management.",
        ), 403

    return None


@app.route("/admin")
@login_required
def administration():
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    organizations = get_all_organizations()

    return render_template(
        "administration.html",
        organizations=organizations,
    )


@app.route("/admin/organizations")
@login_required
def admin_organizations():
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    organizations = get_all_organizations()

    return render_template(
        "admin_organizations.html",
        organizations=organizations,
    )


@app.route("/admin/organizations/create", methods=["GET", "POST"])
@login_required
def admin_organization_create():
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    user = get_current_user()
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip()
        organization_type = request.form.get(
            "organization_type",
            "",
        ).strip().upper()

        if not name:
            error = "Organization name is required."
        elif not slug:
            error = "Organization slug is required."
        elif organization_type not in ORGANIZATION_TYPES:
            error = "Please select a valid organization type."
        else:
            try:
                create_organization(
                    name=name,
                    slug=slug,
                    organization_type=organization_type,
                    created_by=user.id,
                )

                return redirect(url_for("admin_organizations"))

            except OrganizationAlreadyExistsError as exc:
                error = str(exc)

            except ValueError as exc:
                error = str(exc)

    return render_template(
        "admin_organization_create.html",
        organization_types=ORGANIZATION_TYPES,
        error=error,
    )

@app.route("/admin/organizations/<int:organization_id>/edit", methods=["GET", "POST"])
@login_required
def admin_organization_edit(organization_id):
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    organization = get_organization(organization_id)

    if organization is None:
        return render_template(
            "error.html",
            error="The organization was not found.",
        ), 404

    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip()
        organization_type = request.form.get(
            "organization_type",
            "",
        ).strip().upper()

        if not name:
            error = "Organization name is required."
        elif not slug:
            error = "Organization slug is required."
        elif organization_type not in ORGANIZATION_TYPES:
            error = "Please select a valid organization type."
        else:
            try:
                organization = update_organization(
                    organization_id=organization_id,
                    name=name,
                    slug=slug,
                    organization_type=organization_type,
                )

                return redirect(url_for("admin_organizations"))

            except OrganizationAlreadyExistsError as exc:
                error = str(exc)

            except OrganizationNotFoundError as exc:
                return render_template(
                    "error.html",
                    error=str(exc),
                ), 404

            except ValueError as exc:
                error = str(exc)

    return render_template(
        "admin_organization_edit.html",
        organization=organization,
        organization_types=ORGANIZATION_TYPES,
        error=error,
    )

@app.route("/admin/organizations/<int:organization_id>/deactivate", methods=["POST"])
@login_required
def admin_organization_deactivate(organization_id):
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    try:
        deactivate_organization(organization_id)
    except OrganizationNotFoundError as exc:
        return render_template(
            "error.html",
            error=str(exc),
        ), 404

    return redirect(url_for("admin_organizations"))


@app.route("/admin/organizations/<int:organization_id>/activate", methods=["POST"])
@login_required
def admin_organization_activate(organization_id):
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    try:
        activate_organization(organization_id)
    except OrganizationNotFoundError as exc:
        return render_template(
            "error.html",
            error=str(exc),
        ), 404

    return redirect(url_for("admin_organizations"))


@app.route("/admin/organizations/<int:organization_id>/delete", methods=["POST"])
@login_required
def admin_organization_delete(organization_id):
    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    try:
        delete_organization(organization_id)
    except OrganizationNotFoundError as exc:
        return render_template(
            "error.html",
            error=str(exc),
        ), 404

    return redirect(url_for("admin_organizations"))

@app.route("/admin/roles")
@login_required
def admin_roles():
    """Super Administrator view of platform and organization roles."""

    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    roles = get_all_roles_with_permissions()

    return render_template(
        "admin_roles.html",
        roles=roles,
    )


@app.route("/admin/audit-log")
@login_required
def admin_audit_log():
    """Super Administrator view of platform audit events."""

    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    entries = get_audit_log_entries(limit=250)

    return render_template(
        "admin_audit_log.html",
        entries=entries,
    )

@app.route("/admin/users")
@login_required
def admin_users():
    """Super Administrator platform-wide user management."""

    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    users = get_all_users()

    user_rows = []

    for user in users:
        user_rows.append(
            {
                "user": user,
                "platform_role": get_primary_platform_role(user.id),
                "platform_roles": get_user_platform_roles(user.id),
            }
        )

    return render_template(
        "admin_users.html",
        users=user_rows,
        current_user=get_current_user(),
    )


@app.route("/admin/users/create", methods=["GET", "POST"])
@login_required
def admin_user_create():
    """Super Administrator creates platform users."""

    access_denied = _platform_admin_required()
    if access_denied is not None:
        return access_denied

    error = None
    allowed_roles = [
        STANDARD_USER,
        FULL_ADMINISTRATOR,
    ]

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role_name = request.form.get("role_name", "").strip()

        if role_name not in allowed_roles:
            error = "Please select a valid platform role."
        elif not display_name:
            error = "Display name is required."
        elif not username:
            error = "Username is required."
        elif not email:
            error = "Email address is required."
        elif not password:
            error = "Temporary password is required."
        else:
            try:
                user = create_user(
                    email=email,
                    username=username,
                    display_name=display_name,
                    password=password,
                    created_by=get_current_user().id,
                    role_name=role_name,
                )

                return redirect(url_for("admin_users"))

            except UserAlreadyExistsError as exc:
                error = str(exc)
            except ValueError as exc:
                error = str(exc)

    return render_template(
        "admin_user_create.html",
        allowed_roles=allowed_roles,
        error=error,
    )


@app.route("/user-management")
@login_required
def user_management():
    """Full Administrator user management.

    Full Administrators can only see Standard Users.
    Super Administrators can see all platform users here as well.
    """

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()
    current_role = get_primary_platform_role(current_user.id)

    all_users = get_all_users()

    user_rows = []

    for user in all_users:
        platform_role = get_primary_platform_role(user.id)

        if (
            current_role == FULL_ADMINISTRATOR
            and platform_role != STANDARD_USER
        ):
            continue

        user_rows.append(
            {
                "user": user,
                "platform_role": platform_role,
                "platform_roles": get_user_platform_roles(user.id),
            }
        )

    return render_template(
        "user_management.html",
        users=user_rows,
        current_user=current_user,
        current_role=current_role,
    )


@app.route("/user-management/create", methods=["GET", "POST"])
@login_required
def user_management_create():
    """Create a user according to the current platform administrator role."""

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()
    current_role = get_primary_platform_role(current_user.id)

    if current_role == SUPER_ADMINISTRATOR:
        allowed_roles = [
            STANDARD_USER,
            FULL_ADMINISTRATOR,
        ]
    else:
        allowed_roles = [
            STANDARD_USER,
        ]

    error = None
    selected_role = STANDARD_USER

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        selected_role = request.form.get("role_name", "").strip()

        if selected_role not in allowed_roles:
            error = "You do not have permission to create a user with the selected role."
        elif not display_name:
            error = "Display name is required."
        elif not username:
            error = "Username is required."
        elif not email:
            error = "Email address is required."
        elif not password:
            error = "Temporary password is required."
        else:
            try:
                create_user(
                    email=email,
                    username=username,
                    display_name=display_name,
                    password=password,
                    created_by=current_user.id,
                    role_name=selected_role,
                )

                return redirect(url_for("user_management"))

            except UserAlreadyExistsError as exc:
                error = str(exc)
            except ValueError as exc:
                error = str(exc)

    return render_template(
        "user_management_create.html",
        error=error,
        current_role=current_role,
        allowed_roles=allowed_roles,
        selected_role=selected_role,
    )


@app.route("/user-management/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def user_management_edit(user_id):
    """Edit a user according to platform administrator restrictions."""

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()
    current_role = get_primary_platform_role(current_user.id)

    target = get_user_by_id(user_id)

    if target is None:
        return render_template(
            "error.html",
            status_code=404,
            message="User was not found.",
        ), 404

    target_role = get_primary_platform_role(target.id)

    if (
        current_role == FULL_ADMINISTRATOR
        and target_role != STANDARD_USER
    ):
        return render_template(
            "error.html",
            status_code=403,
            message="Full Administrators can only manage Standard Users.",
        ), 403

    error = None

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        if not display_name:
            error = "Display name is required."
        elif not username:
            error = "Username is required."
        elif not email:
            error = "Email address is required."
        else:
            try:
                update_user(
                    actor_user_id=current_user.id,
                    target_user_id=user_id,
                    email=email,
                    username=username,
                    display_name=display_name,
                )

                return redirect(url_for("user_management"))

            except UserAlreadyExistsError as exc:
                error = str(exc)
            except ValueError as exc:
                error = str(exc)
            except PermissionError as exc:
                return render_template(
                    "error.html",
                    status_code=403,
                    message=str(exc),
                ), 403

    return render_template(
        "user_management_edit.html",
        target=target,
        target_role=target_role,
        current_role=current_role,
        error=error,
    )


@app.route(
    "/user-management/<int:user_id>/reset-password",
    methods=["POST"],
)
@login_required
def user_management_reset_password(user_id):
    """Generate a one-time password reset link for an eligible platform user."""

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()
    current_role = get_primary_platform_role(current_user.id)

    target = get_user_by_id(user_id)

    if target is None:
        return render_template(
            "error.html",
            status_code=404,
            message="User was not found.",
        ), 404

    target_role = get_primary_platform_role(target.id)

    if (
        current_role == FULL_ADMINISTRATOR
        and target_role != STANDARD_USER
    ):
        return render_template(
            "error.html",
            status_code=403,
            message="Full Administrators can only manage Standard Users.",
        ), 403

    token, _ = create_password_reset_token(target.id)

    return redirect(
        url_for(
            "reset_password_route",
            token=token,
        )
    )

@app.route(
    "/user-management/<int:user_id>/activate",
    methods=["POST"],
)
@login_required
def user_management_activate(user_id):
    """Activate an eligible platform user."""

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()

    try:
        set_user_active(
            actor_user_id=current_user.id,
            target_user_id=user_id,
            is_active=True,
        )
    except PermissionError as exc:
        return render_template(
            "error.html",
            status_code=403,
            message=str(exc),
        ), 403
    except ValueError as exc:
        return render_template(
            "error.html",
            status_code=404,
            message=str(exc),
        ), 404

    return redirect(url_for("user_management"))


@app.route(
    "/user-management/<int:user_id>/deactivate",
    methods=["POST"],
)
@login_required
def user_management_deactivate(user_id):
    """Deactivate an eligible platform user."""

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()

    try:
        set_user_active(
            actor_user_id=current_user.id,
            target_user_id=user_id,
            is_active=False,
        )
    except PermissionError as exc:
        return render_template(
            "error.html",
            status_code=403,
            message=str(exc),
        ), 403
    except ValueError as exc:
        return render_template(
            "error.html",
            status_code=404,
            message=str(exc),
        ), 404

    return redirect(url_for("user_management"))


@app.route(
    "/user-management/<int:user_id>/delete",
    methods=["POST"],
)
@login_required
def user_management_delete(user_id):
    """Delete an eligible platform user."""

    access_denied = _user_management_required()
    if access_denied is not None:
        return access_denied

    current_user = get_current_user()

    try:
        delete_user(
            actor_user_id=current_user.id,
            target_user_id=user_id,
        )
    except PermissionError as exc:
        return render_template(
            "error.html",
            status_code=403,
            message=str(exc),
        ), 403
    except ValueError as exc:
        return render_template(
            "error.html",
            status_code=404,
            message=str(exc),
        ), 404

    return redirect(url_for("user_management"))

@app.route("/organization/users")
@organization_permission_required("users.view")
def organization_users():
    organization = get_current_organization()

    if organization is None:
        return redirect(url_for("profile"))

    memberships = get_organization_members(organization.id)

    members = []

    for membership in memberships:
        user = get_user_by_id(membership.user_id)
        roles = get_membership_roles(membership.id)

        if user is None:
            continue

        members.append(
            {
                "user": user,
                "membership": membership,
                "roles": roles,
            }
        )

    return render_template(
        "organization_users.html",
        organization=organization,
        members=members,
    )


@app.route("/organization/users/create", methods=["GET", "POST"])
@organization_permission_required("users.create")
def organization_user_create():
    organization = get_current_organization()
    user = get_current_user()

    if organization is None or user is None:
        return redirect(url_for("profile"))

    roles = get_assignable_organization_roles()
    error = None

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        organization_role = request.form.get("organization_role", "").strip().lower()

        allowed_role_names = {
            role["name"]
            for role in roles
        }

        if organization_role not in allowed_role_names:
            error = "Please select a valid organization role."
        else:
            try:
                create_organization_user(
                    organization_id=organization.id,
                    created_by=user.id,
                    email=email,
                    username=username,
                    display_name=display_name,
                    password=password,
                    organization_role=organization_role,
                )

                return redirect(url_for("organization_users"))

            except OrganizationUserCreationError as exc:
                error = str(exc)

            except ValueError as exc:
                error = str(exc)

    return render_template(
        "organization_user_create.html",
        organization=organization,
        roles=roles,
        error=error,
    )

@app.route("/profile")
@login_required
def profile():
    user = get_current_user()
    mfa_status = get_mfa_status(user_id=user.id)
    profile_context = _get_profile_organization_context(user)

    return render_template(
        "profile.html",
        user=user,
        mfa_status=mfa_status,
        mfa_error=None,
        mfa_message=None,
        recovery_codes=None,
        **profile_context,
    )


@app.route("/profile/mfa/enable", methods=["POST"])
@login_required
def profile_mfa_enable():
    user = get_current_user()

    try:
        enrollment = begin_mfa_enrollment(
            user_id=user.id,
        )
    except ValueError as exc:
        return render_template(
            "profile.html",
            user=user,
            mfa_status=get_mfa_status(user_id=user.id),
            mfa_error=str(exc),
            mfa_message=None,
            recovery_codes=None,
        ), 400

    return render_template(
        "mfa_setup.html",
        user=user,
        provisioning_uri=enrollment["provisioning_uri"],
        qr_data_uri=_mfa_qr_data_uri(
            enrollment["provisioning_uri"]
        ),
        secret=enrollment["secret"],
        error=None,
    )


@app.route("/profile/mfa/confirm", methods=["POST"])
@login_required
def profile_mfa_confirm():
    user = get_current_user()

    code = request.form.get(
        "code",
        "",
    ).strip()

    if not code:
        provisioning_uri = request.form.get(
            "provisioning_uri",
            "",
        )

        return render_template(
            "mfa_setup.html",
            user=user,
            provisioning_uri=provisioning_uri,
            qr_data_uri=(
                _mfa_qr_data_uri(provisioning_uri)
                if provisioning_uri
                else ""
            ),
            secret=request.form.get(
                "secret",
                "",
            ),
            error="Enter the 6-digit verification code.",
        ), 400

    try:
        recovery_codes = confirm_mfa_enrollment(
            user_id=user.id,
            code=code,
        )
    except ValueError as exc:
        provisioning_uri = request.form.get(
            "provisioning_uri",
            "",
        )

        return render_template(
            "mfa_setup.html",
            user=user,
            provisioning_uri=provisioning_uri,
            qr_data_uri=(
                _mfa_qr_data_uri(provisioning_uri)
                if provisioning_uri
                else ""
            ),
            secret=request.form.get(
                "secret",
                "",
            ),
            error=str(exc),
        ), 400

    return render_template(
        "profile.html",
        user=user,
        mfa_status=get_mfa_status(user_id=user.id),
        mfa_error=None,
        mfa_message=(
            "MFA has been enabled. Save your recovery codes "
            "before leaving this page."
        ),
        recovery_codes=recovery_codes,
    )


@app.route("/profile/mfa/disable", methods=["POST"])
@login_required
def profile_mfa_disable():
    user = get_current_user()

    password = request.form.get(
        "password",
        "",
    )
    code = request.form.get(
        "code",
        "",
    ).strip()

    try:
        authenticate_user(
            identifier=user.email,
            password=password,
        )
    except InvalidCredentialsError:
        return render_template(
            "profile.html",
            user=user,
            mfa_status=get_mfa_status(user_id=user.id),
            mfa_error="The current password is incorrect.",
            mfa_message=None,
            recovery_codes=None,
        ), 401

    if not verify_mfa_code(
        user_id=user.id,
        code=code,
    ):
        return render_template(
            "profile.html",
            user=user,
            mfa_status=get_mfa_status(user_id=user.id),
            mfa_error="The MFA verification code is invalid.",
            mfa_message=None,
            recovery_codes=None,
        ), 401

    disable_mfa(user_id=user.id)

    return redirect(url_for("profile"))


@app.route("/app")
@login_required
def index():

    return render_template(
        "index.html",
        planets=PLANET_LOOKUP,
    )

@app.route("/galaxy")
def galaxy():

    celestial_context = get_celestial_object_context(
        "milky-way",
        observation_time=datetime.now(timezone.utc),
    )

    return render_template(
        "galaxy.html",
        celestial_context=celestial_context,
    )

@app.route("/solar-system")
def solar_system():

    celestial_context = get_celestial_object_context(
        "solar-system",
        observation_time=datetime.now(timezone.utc),
    )

    return render_template(
        "solar_system.html",
        celestial_context=celestial_context,
    )

@app.route("/ai")
def ai_workspace():
    return render_template(
        "ai.html"
    )

@app.route("/monitoring")
@login_required
def monitoring():
    return render_template(
        "monitoring.html"
    )

@app.route("/overview")
def overview():

    now, results = (
        generate_solar_system_overview()
    )

    return render_template(
        "overview.html",
        now=now,
        results=results,
        ephemeris_source=get_ephemeris_data_source(),
    )

@app.route("/spacecraft")
def spacecraft_tracking_page():

    norad_id = request.args.get(
        "norad_id",
        "",
    ).strip()

    if not norad_id.isdigit():

        return render_template(
            "error.html",
            message="NORAD ID must be numeric.",
        )

    try:

        result = track_spacecraft_by_norad(
            norad_id
        )

    except SpacecraftNotFoundError:

        return render_template(
            "error.html",
            message="Spacecraft was not found.",
        )

    except SpacecraftServiceError:

        return render_template(
            "error.html",
            message=(
                "Spacecraft data service "
                "is currently unavailable."
            ),
        )

    celestial_context = None

    canonical_object_id = (
        f"spacecraft:{norad_id}"
    )

    if get_celestial_object(
        canonical_object_id
    ) is not None:

        celestial_context = (
            get_celestial_object_context(
                canonical_object_id,
                observation_time=datetime.fromisoformat(
                    result["observation_time"]
                ),
            )
        )

    return render_template(
        "spacecraft.html",
        spacecraft=result,
        norad_id=norad_id,
        celestial_context=celestial_context,
    )

@app.route("/asteroid")
def asteroid_tracking_page():

    designation = request.args.get(
        "designation",
        "",
    ).strip()

    if not designation:

        return render_template(
            "error.html",
            message="Asteroid designation is required.",
        )

    try:

        from astrosphere.astronomy.asteroids import (
            track_asteroid,
        )

        result = track_asteroid(
            designation
        )

    except Exception as error:

        return render_template(
            "error.html",
            message=str(error),
        )

    celestial_context = None

    canonical_object_id = (
        f"asteroid:{designation}"
    )

    if get_celestial_object(
        canonical_object_id
    ) is not None:

        celestial_context = (
            get_celestial_object_context(
                canonical_object_id,
                observation_time=datetime.fromisoformat(
                    result["observation_time"]
                ),
            )
        )

    return render_template(
        "asteroid.html",
        asteroid=result,
        celestial_context=celestial_context,
    )

@app.route("/celestial/<path:object_id>")
def celestial_object_page(object_id):

    try:
        celestial_context = get_celestial_object_context(
            object_id,
            observation_time=datetime.now(timezone.utc),
        )

    except ValueError:
        return render_template(
            "error.html",
            message="Celestial object was not found.",
        )

    return render_template(
        "celestial_object.html",
        celestial_context=celestial_context,
    )

@app.route("/planet/<planet_name>")
def planet_detail(planet_name):

    if planet_name not in PLANET_LOOKUP:

        return render_template(
            "error.html",
            message="Invalid planetary body.",
        )

    planet = PLANET_LOOKUP[
        planet_name
    ]

    solar_system = load_solar_system()

    now = get_current_time()

    sun = solar_system["sun"]
    earth = solar_system["earth"]

    body = solar_system[
        planet.skyfield_name
    ]

    sun_position = sun.at(now)

    earth_position = earth.at(now)

    body_position = body.at(now)

    celestial_context = get_celestial_object_context(
        planet_name,
        observation_time=now,
    )

    scientific_data = celestial_context["scientific_data"]


    distance_from_sun = calculate_distance_km(
        body_position,
        sun_position,
    )


    distance_from_earth = calculate_distance_km(
        body_position,
        earth_position,
    )


    velocity_relative_to_earth = (
        calculate_relative_velocity_km_s(
            earth_position,
            body_position,
        )
    )


    return render_template(
        "planet.html",

        planet=planet,

        now=now,

        scientific_data=scientific_data,

        celestial_context=celestial_context,

        distance_from_sun=distance_from_sun,

        distance_from_earth=distance_from_earth,

        velocity_relative_to_earth=(
            velocity_relative_to_earth
        ),
    )


@app.route("/analyze", methods=["POST"])
def analyze():

    reference_name = request.form.get(
        "reference",
        ""
    ).strip().lower()

    target_name = request.form.get(
        "target",
        ""
    ).strip().lower()

    start_date_text = request.form.get(
        "start_date",
        ""
    ).strip()

    months_text = request.form.get(
        "period",
        ""
    ).strip()

    interval_text = request.form.get(
        "interval",
        ""
    ).strip()


    # ---------------------------------------------------------
    # VALIDATE REFERENCE BODY
    # ---------------------------------------------------------

    if reference_name not in PLANET_LOOKUP:

        return render_template(
            "error.html",
            message="Invalid reference body.",
        )


    # ---------------------------------------------------------
    # VALIDATE TARGET BODY
    # ---------------------------------------------------------

    if target_name not in PLANET_LOOKUP:

        return render_template(
            "error.html",
            message="Invalid target body.",
        )


    # ---------------------------------------------------------
    # VALIDATE REFERENCE / TARGET
    # ---------------------------------------------------------

    if reference_name == target_name:

        return render_template(
            "error.html",
            message=(
                "Reference body and target body "
                "cannot be the same."
            ),
        )


    # ---------------------------------------------------------
    # PARSE START DATE
    # ---------------------------------------------------------

    try:

        analysis_date = datetime.strptime(
            start_date_text,
            "%Y-%m-%d",
        ).replace(
            tzinfo=timezone.utc
        )

    except ValueError:

        return render_template(
            "error.html",
            message=(
                "Invalid date. "
                "Please provide a valid date."
            ),
        )


    # ---------------------------------------------------------
    # PARSE ANALYSIS PARAMETERS
    # ---------------------------------------------------------

    try:

        months = int(months_text)

        interval_days = int(interval_text)

    except ValueError:

        return render_template(
            "error.html",
            message="Invalid analysis parameters.",
        )


    # ---------------------------------------------------------
    # GET PLANETARY OBJECTS
    # ---------------------------------------------------------

    reference_body = PLANET_LOOKUP[
        reference_name
    ]

    target_body = PLANET_LOOKUP[
        target_name
    ]


    # ---------------------------------------------------------
    # CREATE ANALYSIS CONFIGURATION
    # ---------------------------------------------------------

    config = AnalysisConfig(
        start_date=analysis_date,
        months=months,
        interval_days=interval_days,
        reference_body=reference_body,
    )


    # ---------------------------------------------------------
    # RUN ORBITAL ANALYSIS
    # ---------------------------------------------------------

    try:

        results = analyze_body_distance(
            reference_body_name=(
                config.reference_body.skyfield_name
            ),
            target_body_name=(
                target_body.skyfield_name
            ),
            start_date=config.start_date,
            months=config.months,
            interval_days=config.interval_days,
        )

    except ValueError as error:

        return render_template(
            "error.html",
            message=str(error),
        )


    # ---------------------------------------------------------
    # CHECK RESULTS
    # ---------------------------------------------------------

    if not results:

        return render_template(
            "error.html",
            message="No orbital data was returned.",
        )


    # ---------------------------------------------------------
    # CLOSEST / FARTHEST
    # ---------------------------------------------------------

    closest = min(
        results,
        key=lambda result: result["distance_km"],
    )

    farthest = max(
        results,
        key=lambda result: result["distance_km"],
    )


    # ---------------------------------------------------------
    # BASIC DISTANCE STATISTICS
    # ---------------------------------------------------------

    initial_km = results[0]["distance_km"]

    final_km = results[-1]["distance_km"]

    minimum_km = closest["distance_km"]

    maximum_km = farthest["distance_km"]


    variation_km = (
        maximum_km - minimum_km
    )


    average_km = sum(
        result["distance_km"]
        for result in results
    ) / len(results)


    # ---------------------------------------------------------
    # DISTANCE CHANGE
    # ---------------------------------------------------------

    distance_change_km = (
        final_km - initial_km
    )


    # ---------------------------------------------------------
    # PERCENTAGE CHANGE
    # ---------------------------------------------------------

    if initial_km != 0:

        percentage_change = (
            distance_change_km
            / initial_km
        ) * 100

    else:

        percentage_change = 0.0


       # ---------------------------------------------------------
    # DETERMINE TREND
    # ---------------------------------------------------------

    if distance_change_km < 0:

        trend = "Getting closer"

    elif distance_change_km > 0:

        trend = "Getting farther apart"

    else:

        trend = "No overall change"


    # ---------------------------------------------------------
    # RELATIVE VELOCITY STATISTICS
    # ---------------------------------------------------------

    initial_velocity_km_s = (
        results[0]["relative_velocity_km_s"]
    )

    final_velocity_km_s = (
        results[-1]["relative_velocity_km_s"]
    )

    minimum_velocity_km_s = min(
        result["relative_velocity_km_s"]
        for result in results
    )

    maximum_velocity_km_s = max(
        result["relative_velocity_km_s"]
        for result in results
    )

    average_velocity_km_s = sum(
        result["relative_velocity_km_s"]
        for result in results
    ) / len(results)

    velocity_change_km_s = (
        final_velocity_km_s
        - initial_velocity_km_s
    )

    if initial_velocity_km_s != 0:

        velocity_percentage_change = (
            velocity_change_km_s
            / initial_velocity_km_s
        ) * 100

    else:

        velocity_percentage_change = 0.0


    if velocity_change_km_s < 0:

        velocity_trend = "Slowing down"

    elif velocity_change_km_s > 0:

        velocity_trend = "Speeding up"

    else:

        velocity_trend = "No overall change"


    # ---------------------------------------------------------
    # PREPARE CHART DATA
    # ---------------------------------------------------------

    chart_dates = [
        result["date"].strftime("%Y-%m-%d")
        for result in results
    ]

    chart_distances = [
        result["distance_km"] / 1_000_000
        for result in results
    ]

    chart_velocities = [
        result["relative_velocity_km_s"]
        for result in results
    ]


    # ---------------------------------------------------------
    # RENDER RESULTS PAGE
    # ---------------------------------------------------------

    return render_template(
        "results.html",

        reference_body=reference_body,
        target_body=target_body,

        config=config,

        results=results,

        closest=closest,
        farthest=farthest,

        initial_km=initial_km,
        final_km=final_km,

        minimum_km=minimum_km,
        maximum_km=maximum_km,

        variation_km=variation_km,
        average_km=average_km,

        distance_change_km=distance_change_km,
        percentage_change=percentage_change,

        trend=trend,

        initial_velocity_km_s=initial_velocity_km_s,
        final_velocity_km_s=final_velocity_km_s,

        minimum_velocity_km_s=minimum_velocity_km_s,
        maximum_velocity_km_s=maximum_velocity_km_s,

        average_velocity_km_s=average_velocity_km_s,

        velocity_change_km_s=velocity_change_km_s,
        velocity_percentage_change=velocity_percentage_change,

        velocity_trend=velocity_trend,

        chart_dates=chart_dates,
        chart_distances=chart_distances,
        chart_velocities=chart_velocities,
    )
 
if __name__ == "__main__":

    app.run(
        debug=AppConfig.DEBUG,
        host=AppConfig.HOST,
        port=AppConfig.PORT,
    )
