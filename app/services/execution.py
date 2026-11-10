"""Atomic execution engine applying approved operations to database tables."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.pending_operation import PendingOperation
from app.database.models.inventory import InventoryItem
from app.database.models.bill import Bill
from app.security.authentication import UserContext
from app.security.tenant import scope_query_to_tenant
from app.services.audit import log_audit_event
from app.core.exceptions import DatabaseTransactionError


def execute_operation(
    db: Session,
    context: UserContext,
    pending_op: PendingOperation,
) -> Dict[str, Any]:
    """
    Apply a pending operation atomically to the database.
    Guarantees strict tenant scoping and emits audit trail records.
    """
    target = pending_op.target_resource
    op_type = pending_op.operation_type
    changes = pending_op.proposed_changes
    filter_criteria = pending_op.filter_criteria

    try:
        updated_records = 0

        if target == "inventory_items":
            stmt = sa.select(InventoryItem)
            stmt = scope_query_to_tenant(stmt, InventoryItem, context.hospital_id)

            if "id" in filter_criteria:
                stmt = stmt.where(InventoryItem.id == filter_criteria["id"])
            if "sku" in filter_criteria:
                stmt = stmt.where(InventoryItem.sku == filter_criteria["sku"])
            if "category" in filter_criteria:
                stmt = stmt.where(InventoryItem.category == filter_criteria["category"])
            if "batch_number" in filter_criteria:
                stmt = stmt.where(InventoryItem.batch_number == filter_criteria["batch_number"])

            items = list(db.execute(stmt).scalars().all())

            for item in items:
                before_state = {
                    "id": str(item.id),
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "location": item.location,
                }

                if op_type == "inventory.update":
                    if "quantity" in changes:
                        item.quantity = changes["quantity"]
                    if "unit_price" in changes:
                        item.unit_price = Decimal(str(changes["unit_price"]))
                    if "location" in changes:
                        item.location = changes["location"]

                elif op_type == "inventory.delete":
                    db.delete(item)

                after_state = (
                    None
                    if op_type == "inventory.delete"
                    else {
                        "id": str(item.id),
                        "quantity": item.quantity,
                        "unit_price": str(item.unit_price),
                        "location": item.location,
                    }
                )

                log_audit_event(
                    db=db,
                    hospital_id=context.hospital_id,
                    user_id=context.user_id,
                    action=op_type,
                    resource_type="inventory_items",
                    resource_id=str(item.id),
                    status="SUCCESS",
                    before_state=before_state,
                    after_state=after_state,
                    metadata_info={"pending_operation_id": str(pending_op.id)},
                )
                updated_records += 1

        elif target == "bills":
            stmt = sa.select(Bill)
            stmt = scope_query_to_tenant(stmt, Bill, context.hospital_id)

            if "id" in filter_criteria:
                stmt = stmt.where(Bill.id == filter_criteria["id"])
            if "bill_number" in filter_criteria:
                stmt = stmt.where(Bill.bill_number == filter_criteria["bill_number"])

            bills = list(db.execute(stmt).scalars().all())

            for bill in bills:
                before_state = {
                    "id": str(bill.id),
                    "discount_pct": str(bill.discount_pct),
                    "final_amount": str(bill.final_amount),
                    "status": bill.status,
                }

                if op_type == "bills.discount":
                    disc = Decimal(str(changes["discount_pct"]))
                    bill.discount_pct = disc
                    bill.final_amount = bill.total_amount * (1 - (disc / Decimal("100")))

                elif op_type == "bills.update_status":
                    bill.status = changes["status"]
                    if "notes" in changes and changes["notes"]:
                        bill.notes = (bill.notes or "") + f"\n[{datetime.now(timezone.utc)}] {changes['notes']}"

                after_state = {
                    "id": str(bill.id),
                    "discount_pct": str(bill.discount_pct),
                    "final_amount": str(bill.final_amount),
                    "status": bill.status,
                }

                log_audit_event(
                    db=db,
                    hospital_id=context.hospital_id,
                    user_id=context.user_id,
                    action=op_type,
                    resource_type="bills",
                    resource_id=str(bill.id),
                    status="SUCCESS",
                    before_state=before_state,
                    after_state=after_state,
                    metadata_info={"pending_operation_id": str(pending_op.id)},
                )
                updated_records += 1

        return {
            "status": "success",
            "operation_id": str(pending_op.id),
            "updated_records": updated_records,
        }

    except Exception as exc:
        db.rollback()
        log_audit_event(
            db=db,
            hospital_id=context.hospital_id,
            user_id=context.user_id,
            action=op_type,
            resource_type=target,
            status="FAILED",
            metadata_info={"error": str(exc), "pending_operation_id": str(pending_op.id)},
        )
        raise DatabaseTransactionError(f"Failed to execute operation atomically: {str(exc)}")
