"""Bills domain query operations with tenant scoping and record-level visibility enforcement."""

import uuid
from typing import List, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.bill import Bill
from app.security.authentication import UserContext
from app.security.tenant import scope_query_to_tenant
from app.security.permissions import StandardPermission
from app.security.constraints import check_bill_read_scope
from app.core.exceptions import PermissionDeniedError, EntityNotFoundError


def list_bills(
    db: Session,
    context: UserContext,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Bill]:
    """
    Query bills within the user's hospital tenant.
    Enforces bills.read permission and record visibility constraints (e.g. Front Desk own_records).
    """
    if not context.has_permission(StandardPermission.BILLS_READ.value):
        raise PermissionDeniedError("User lacks bills.read permission.")

    stmt = sa.select(Bill)
    stmt = scope_query_to_tenant(stmt, Bill, context.hospital_id)

    # Check for record-level scope constraint
    scope = context.get_constraint(StandardPermission.BILLS_READ.value, "scope")
    if scope == "own_records":
        stmt = stmt.where(Bill.created_by_user_id == context.user_id)

    if status:
        stmt = stmt.where(Bill.status == status)

    stmt = stmt.order_by(Bill.bill_date.desc()).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


def get_bill(
    db: Session,
    context: UserContext,
    bill_id: uuid.UUID,
) -> Bill:
    """
    Retrieve a specific bill ensuring tenant boundary and record-level scope checks.
    """
    if not context.has_permission(StandardPermission.BILLS_READ.value):
        raise PermissionDeniedError("User lacks bills.read permission.")

    stmt = sa.select(Bill).where(
        Bill.id == bill_id,
        Bill.hospital_id == context.hospital_id,
    )
    bill = db.execute(stmt).scalar_one_or_none()
    if not bill:
        raise EntityNotFoundError(f"Bill '{bill_id}' not found.")

    if not check_bill_read_scope(context, bill.created_by_user_id):
        raise PermissionDeniedError("Access denied: You can only view bills you created.")

    return bill
