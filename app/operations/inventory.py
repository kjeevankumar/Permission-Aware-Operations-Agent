"""Inventory domain query operations with tenant scoping and constraint enforcement."""

import uuid
from typing import List, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.inventory import InventoryItem
from app.security.authentication import UserContext
from app.security.tenant import scope_query_to_tenant
from app.security.permissions import StandardPermission
from app.core.exceptions import PermissionDeniedError, EntityNotFoundError
from app.schemas.inventory import InventoryFilter
from app.utils.date_resolver import get_expiry_window


def list_inventory_items(
    db: Session,
    context: UserContext,
    filters: Optional[InventoryFilter] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[InventoryItem]:
    """
    Query inventory items strictly scoped to the user's hospital tenant.
    Enforces inventory.read permission.
    """
    if not context.has_permission(StandardPermission.INVENTORY_READ.value):
        raise PermissionDeniedError("User lacks inventory.read permission.")

    stmt = sa.select(InventoryItem)
    stmt = scope_query_to_tenant(stmt, InventoryItem, context.hospital_id)

    if filters:
        if filters.category:
            stmt = stmt.where(InventoryItem.category == filters.category)
        if filters.search:
            pattern = f"%{filters.search}%"
            stmt = stmt.where(
                sa.or_(
                    InventoryItem.name.ilike(pattern),
                    InventoryItem.sku.ilike(pattern),
                    InventoryItem.batch_number.ilike(pattern),
                )
            )
        if filters.low_stock:
            stmt = stmt.where(InventoryItem.quantity <= InventoryItem.reorder_level)
        if filters.expiring_within_days:
            start_date, end_date = get_expiry_window(filters.expiring_within_days)
            stmt = stmt.where(InventoryItem.expiry_date.between(start_date, end_date))

    stmt = stmt.order_by(InventoryItem.name.asc()).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_inventory_item(
    db: Session,
    context: UserContext,
    item_id: uuid.UUID,
) -> InventoryItem:
    """
    Retrieve a specific inventory item by ID within the tenant.
    """
    if not context.has_permission(StandardPermission.INVENTORY_READ.value):
        raise PermissionDeniedError("User lacks inventory.read permission.")

    stmt = sa.select(InventoryItem).where(
        InventoryItem.id == item_id,
        InventoryItem.hospital_id == context.hospital_id,
    )
    item = db.execute(stmt).scalar_one_or_none()
    if not item:
        raise EntityNotFoundError(f"Inventory item '{item_id}' not found.")
    return item
