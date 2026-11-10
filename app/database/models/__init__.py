"""Package exposing all database models for easy import and metadata registration."""

from app.database.models.hospital import Hospital
from app.database.models.role import Role
from app.database.models.permission import Permission, RolePermission
from app.database.models.user import User, UserRole, UserPermissionOverride
from app.database.models.inventory import InventoryItem
from app.database.models.bill import Bill
from app.database.models.audit import AuditLog
from app.database.models.pending_operation import PendingOperation

__all__ = [
    "Hospital",
    "Role",
    "Permission",
    "RolePermission",
    "User",
    "UserRole",
    "UserPermissionOverride",
    "InventoryItem",
    "Bill",
    "AuditLog",
    "PendingOperation",
]
