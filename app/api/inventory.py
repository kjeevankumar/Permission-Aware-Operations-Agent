"""Inventory query API routes."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user_context, require_permission
from app.security.authentication import UserContext
from app.schemas.inventory import InventoryItemRead, InventoryFilter
from app.operations.inventory import list_inventory_items, get_inventory_item
from app.core.exceptions import AppException, http_exception_from_app_error

router = APIRouter(prefix="/inventory", tags=["Pharmacy & Inventory"])


@router.get("", response_model=List[InventoryItemRead])
def get_inventory(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name, SKU, or batch"),
    low_stock: Optional[bool] = Query(None, description="Filter items at or below reorder level"),
    expiring_within_days: Optional[int] = Query(None, ge=1, description="Expiring within N days"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    context: UserContext = Depends(require_permission("inventory.read")),
    db: Session = Depends(get_db),
) -> List[InventoryItemRead]:
    """
    List inventory items strictly scoped to the authenticated user's hospital tenant.
    Enforces inventory.read permission and tenant boundaries.
    """
    try:
        filters = InventoryFilter(
            category=category,
            search=search,
            low_stock=low_stock,
            expiring_within_days=expiring_within_days,
        )
        items = list_inventory_items(
            db=db,
            context=context,
            filters=filters,
            limit=limit,
            offset=offset,
        )
        return items
    except AppException as exc:
        raise http_exception_from_app_error(exc)


@router.get("/{item_id}", response_model=InventoryItemRead)
def get_single_inventory_item(
    item_id: uuid.UUID,
    context: UserContext = Depends(require_permission("inventory.read")),
    db: Session = Depends(get_db),
) -> InventoryItemRead:
    """Retrieve details for a specific inventory item within the tenant."""
    try:
        return get_inventory_item(db=db, context=context, item_id=item_id)
    except AppException as exc:
        raise http_exception_from_app_error(exc)
