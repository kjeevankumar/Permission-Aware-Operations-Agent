"""Users and access control operations with tenant boundaries."""

import uuid
from typing import List, Dict, Any, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.user import User, UserPermissionOverride
from app.database.models.permission import Permission
from app.security.authentication import UserContext
from app.security.tenant import scope_query_to_tenant, verify_tenant_boundary
from app.security.permissions import StandardPermission
from app.core.exceptions import PermissionDeniedError, EntityNotFoundError


def list_hospital_users(
    db: Session,
    context: UserContext,
) -> List[User]:
    """
    List all user accounts belonging to the authenticated user's hospital tenant.
    Requires users.read permission.
    """
    if not context.has_permission(StandardPermission.USERS_READ.value):
        raise PermissionDeniedError("User lacks users.read permission.")

    stmt = sa.select(User)
    stmt = scope_query_to_tenant(stmt, User, context.hospital_id)
    stmt = stmt.order_by(User.full_name.asc())
    return list(db.execute(stmt).scalars().all())


def get_hospital_user(
    db: Session,
    context: UserContext,
    user_id: uuid.UUID,
) -> User:
    """
    Retrieve user details ensuring tenant isolation.
    """
    if not context.has_permission(StandardPermission.USERS_READ.value):
        raise PermissionDeniedError("User lacks users.read permission.")

    stmt = sa.select(User).where(
        User.id == user_id,
        User.hospital_id == context.hospital_id,
    )
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        raise EntityNotFoundError(f"User '{user_id}' not found.")
    return user


def set_user_permission_override(
    db: Session,
    context: UserContext,
    target_user_id: uuid.UUID,
    permission_code: str,
    is_granted: bool,
    constraints_override: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
) -> UserPermissionOverride:
    """
    Grant or revoke a specific permission for a single user without altering role definitions.
    Requires users.manage_access permission.
    """
    if not context.has_permission(StandardPermission.USERS_MANAGE_ACCESS.value):
        raise PermissionDeniedError("User lacks users.manage_access permission.")

    target_user = db.execute(sa.select(User).where(User.id == target_user_id)).scalar_one_or_none()
    if not target_user:
        raise EntityNotFoundError(f"Target user '{target_user_id}' not found.")

    verify_tenant_boundary(target_user, context.hospital_id)

    perm_stmt = sa.select(Permission).where(Permission.code == permission_code)
    permission = db.execute(perm_stmt).scalar_one_or_none()
    if not permission:
        raise EntityNotFoundError(f"Permission code '{permission_code}' is not recognized.")

    # Check for existing override
    override_stmt = sa.select(UserPermissionOverride).where(
        UserPermissionOverride.user_id == target_user_id,
        UserPermissionOverride.permission_id == permission.id,
    )
    override = db.execute(override_stmt).scalar_one_or_none()

    if override:
        override.is_granted = is_granted
        override.constraints_override = constraints_override
        override.reason = reason
        override.created_by_user_id = context.user_id
    else:
        override = UserPermissionOverride(
            hospital_id=context.hospital_id,
            user_id=target_user_id,
            permission_id=permission.id,
            is_granted=is_granted,
            constraints_override=constraints_override,
            reason=reason,
            created_by_user_id=context.user_id,
        )
        db.add(override)

    db.commit()
    return override
