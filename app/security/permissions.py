"""Role-Based Access Control and Permission Resolution Engine."""

from enum import Enum
from typing import Dict, Any, Set
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.user import User, UserRole, UserPermissionOverride
from app.database.models.permission import RolePermission, Permission


class StandardPermission(str, Enum):
    """Catalog of supported system permissions (strictly excluding bills.delete)."""

    INVENTORY_READ = "inventory.read"
    INVENTORY_CREATE = "inventory.create"
    INVENTORY_UPDATE = "inventory.update"
    INVENTORY_DELETE = "inventory.delete"

    BILLS_READ = "bills.read"
    BILLS_CREATE = "bills.create"
    BILLS_DISCOUNT = "bills.discount"
    BILLS_UPDATE_STATUS = "bills.update_status"

    USERS_READ = "users.read"
    USERS_MANAGE_ACCESS = "users.manage_access"

    AUDIT_READ = "audit.read"
    OPERATIONS_PREVIEW = "operations.preview"
    OPERATIONS_CONFIRM = "operations.confirm"
    REPORTS_READ = "reports.read"


ALL_PERMISSIONS: Set[str] = {p.value for p in StandardPermission}


def resolve_effective_permissions(db: Session, user: User) -> Dict[str, Dict[str, Any]]:
    """
    Resolve effective permissions for a user:
    1. Query all role permissions granted to user's assigned roles.
    2. Merge constraints across multiple roles (e.g., take most permissive constraint).
    3. Apply individual user permission overrides:
       - If is_granted is False, revokes permission entirely.
       - If is_granted is True, grants permission and merges/applies constraints_override.
    """
    # 1. Fetch user's assigned roles
    role_stmt = (
        sa.select(RolePermission, Permission.code)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(UserRole.user_id == user.id)
    )
    role_results = db.execute(role_stmt).all()

    effective_permissions: Dict[str, Dict[str, Any]] = {}

    for rp, perm_code in role_results:
        existing_constraints = effective_permissions.get(perm_code, {})
        new_constraints = dict(rp.constraints) if rp.constraints else {}

        # Merge constraints intelligently:
        # e.g., max_rows: take max, max_discount_pct: take max
        merged = dict(existing_constraints)
        for k, v in new_constraints.items():
            if k not in merged:
                merged[k] = v
            else:
                if isinstance(v, (int, float)) and isinstance(merged[k], (int, float)):
                    merged[k] = max(merged[k], v)
                else:
                    merged[k] = v
        effective_permissions[perm_code] = merged

    # 2. Fetch and apply user-specific overrides
    override_stmt = (
        sa.select(UserPermissionOverride, Permission.code)
        .join(Permission, Permission.id == UserPermissionOverride.permission_id)
        .where(UserPermissionOverride.user_id == user.id)
    )
    overrides = db.execute(override_stmt).all()

    for override, perm_code in overrides:
        if not override.is_granted:
            # Explicit denial / revocation
            effective_permissions.pop(perm_code, None)
        else:
            # Explicit grant or constraint override
            current = effective_permissions.get(perm_code, {})
            if override.constraints_override:
                current.update(override.constraints_override)
            effective_permissions[perm_code] = current

    return effective_permissions
