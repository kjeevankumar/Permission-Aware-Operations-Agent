"""Authentication management and user security context builder."""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.user import User, UserRole
from app.database.models.role import Role
from app.core.security import verify_password
from app.core.exceptions import AuthenticationError
from app.security.permissions import resolve_effective_permissions


@dataclass
class UserContext:
    """Immutable runtime security context derived solely from database state and verified token."""

    user_id: uuid.UUID
    hospital_id: uuid.UUID
    username: str
    email: str
    full_name: str
    active_roles: List[str] = field(default_factory=list)
    permissions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    account_status: str = "active"

    def has_permission(self, permission_code: str) -> bool:
        """Check if context contains the specified permission code."""
        return permission_code in self.permissions

    def get_constraint(
        self,
        permission_code: str,
        constraint_key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve a specific constraint parameter for a given permission."""
        perm_constraints = self.permissions.get(permission_code, {})
        return perm_constraints.get(constraint_key, default)


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate a user by username and password.
    Returns the User entity if valid, None otherwise.
    """
    stmt = sa.select(User).where(User.username == username)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def resolve_user_context(db: Session, user_id: uuid.UUID) -> UserContext:
    """
    Construct the authenticated security context for a user by querying the database.
    This guarantees hospital_id, roles, and permissions are never forged by the client.
    """
    stmt = (
        sa.select(User)
        .where(User.id == user_id)
    )
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        raise AuthenticationError("User not found.")

    if not user.is_active:
        raise AuthenticationError("User account is inactive or suspended.")

    # Fetch active roles
    roles_stmt = (
        sa.select(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    )
    role_names = list(db.execute(roles_stmt).scalars().all())

    # Resolve effective permissions including role constraints and user overrides
    effective_permissions = resolve_effective_permissions(db, user)

    return UserContext(
        user_id=user.id,
        hospital_id=user.hospital_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        active_roles=role_names,
        permissions=effective_permissions,
        account_status="active" if user.is_active else "inactive",
    )
