"""Security package providing authentication, tenant isolation, permissions, and constraint checks."""

from app.security.authentication import UserContext, authenticate_user, resolve_user_context
from app.security.permissions import (
    StandardPermission,
    ALL_PERMISSIONS,
    resolve_effective_permissions,
)
from app.security.constraints import (
    validate_inventory_update_constraints,
    validate_bill_discount_constraints,
    check_bill_read_scope,
)
from app.security.tenant import scope_query_to_tenant, verify_tenant_boundary

__all__ = [
    "UserContext",
    "authenticate_user",
    "resolve_user_context",
    "StandardPermission",
    "ALL_PERMISSIONS",
    "resolve_effective_permissions",
    "validate_inventory_update_constraints",
    "validate_bill_discount_constraints",
    "check_bill_read_scope",
    "scope_query_to_tenant",
    "verify_tenant_boundary",
]
