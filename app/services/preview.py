"""Operation preview and dry-run diff generation service."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.config import settings
from app.database.models.pending_operation import PendingOperation
from app.database.models.inventory import InventoryItem
from app.database.models.bill import Bill
from app.security.authentication import UserContext
from app.security.constraints import (
    validate_inventory_update_constraints,
    validate_bill_discount_constraints,
)
from app.security.tenant import scope_query_to_tenant
from app.core.exceptions import PermissionDeniedError, EntityNotFoundError


def create_operation_preview(
    db: Session,
    context: UserContext,
    operation_type: str,
    target_resource: str,
    filter_criteria: Dict[str, Any],
    proposed_changes: Dict[str, Any],
) -> PendingOperation:
    """
    Stage an operation preview:
    1. Verify permissions and constraints against proposed changes.
    2. Query impacted rows strictly scoped to the user's hospital.
    3. Generate the before/after state diff.
    4. Store in pending_operations with TTL.
    """
    impacted_rows_diff = []
    impacted_count = 0

    if target_resource == "inventory_items":
        # Check permissions
        if not context.has_permission(operation_type):
            raise PermissionDeniedError(f"User lacks required permission '{operation_type}'.")

        stmt = sa.select(InventoryItem)
        stmt = scope_query_to_tenant(stmt, InventoryItem, context.hospital_id)

        # Apply basic filters
        if "id" in filter_criteria:
            stmt = stmt.where(InventoryItem.id == filter_criteria["id"])
        if "sku" in filter_criteria:
            stmt = stmt.where(InventoryItem.sku == filter_criteria["sku"])
        if "category" in filter_criteria:
            stmt = stmt.where(InventoryItem.category == filter_criteria["category"])
        if "batch_number" in filter_criteria:
            stmt = stmt.where(InventoryItem.batch_number == filter_criteria["batch_number"])

        items = list(db.execute(stmt).scalars().all())
        impacted_count = len(items)

        # Validate constraints
        if operation_type == "inventory.update":
            validate_inventory_update_constraints(context, impacted_count)

        for item in items:
            before = {
                "id": str(item.id),
                "sku": item.sku,
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            }
            after = dict(before)
            for k, v in proposed_changes.items():
                if k in after:
                    after[k] = v
            impacted_rows_diff.append({"id": str(item.id), "before": before, "after": after})

    elif target_resource == "bills":
        if not context.has_permission(operation_type):
            raise PermissionDeniedError(f"User lacks required permission '{operation_type}'.")

        stmt = sa.select(Bill)
        stmt = scope_query_to_tenant(stmt, Bill, context.hospital_id)

        if "id" in filter_criteria:
            stmt = stmt.where(Bill.id == filter_criteria["id"])
        if "bill_number" in filter_criteria:
            stmt = stmt.where(Bill.bill_number == filter_criteria["bill_number"])

        bills = list(db.execute(stmt).scalars().all())
        impacted_count = len(bills)

        if operation_type == "bills.discount":
            discount_pct = proposed_changes.get("discount_pct", 0)
            from decimal import Decimal
            validate_bill_discount_constraints(context, Decimal(str(discount_pct)))

        for bill in bills:
            before = {
                "id": str(bill.id),
                "bill_number": bill.bill_number,
                "total_amount": str(bill.total_amount),
                "discount_pct": str(bill.discount_pct),
                "final_amount": str(bill.final_amount),
                "status": bill.status,
            }
            after = dict(before)
            if "discount_pct" in proposed_changes:
                disc = Decimal(str(proposed_changes["discount_pct"]))
                after["discount_pct"] = str(disc)
                after["final_amount"] = str(bill.total_amount * (1 - (disc / Decimal("100"))))
            if "status" in proposed_changes:
                after["status"] = proposed_changes["status"]

            impacted_rows_diff.append({"id": str(bill.id), "before": before, "after": after})

    else:
        raise EntityNotFoundError(f"Unsupported target resource '{target_resource}'.")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.PENDING_OPERATION_TTL_MINUTES)

    pending_op = PendingOperation(
        hospital_id=context.hospital_id,
        user_id=context.user_id,
        operation_type=operation_type,
        target_resource=target_resource,
        filter_criteria=filter_criteria,
        proposed_changes=proposed_changes,
        impacted_row_count=impacted_count,
        preview_diff={"diff": impacted_rows_diff},
        status="pending",
        expires_at=expires_at,
    )
    db.add(pending_op)
    db.flush()
    return pending_op
