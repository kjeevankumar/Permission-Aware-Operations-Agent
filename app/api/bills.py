"""Billing and patient invoice API routes."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.dependencies import get_current_user_context, require_permission
from app.security.authentication import UserContext
from app.schemas.bill import BillRead
from app.operations.bills import list_bills, get_bill
from app.core.exceptions import AppException, http_exception_from_app_error

router = APIRouter(prefix="/bills", tags=["Hospital Billing"])


@router.get("", response_model=List[BillRead])
def get_bills(
    status: Optional[str] = Query(None, description="Filter by bill status (paid, pending, draft, cancelled, disputed)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    context: UserContext = Depends(require_permission("bills.read")),
    db: Session = Depends(get_db),
) -> List[BillRead]:
    """
    List billing records scoped to the user's hospital tenant.
    Enforces bills.read permission and record visibility rules (e.g. Front Desk own_records scope).
    """
    try:
        bills = list_bills(
            db=db,
            context=context,
            status=status,
            limit=limit,
            offset=offset,
        )
        return bills
    except AppException as exc:
        raise http_exception_from_app_error(exc)


@router.get("/{bill_id}", response_model=BillRead)
def get_single_bill(
    bill_id: uuid.UUID,
    context: UserContext = Depends(require_permission("bills.read")),
    db: Session = Depends(get_db),
) -> BillRead:
    """Retrieve details of a single bill within the tenant."""
    try:
        return get_bill(db=db, context=context, bill_id=bill_id)
    except AppException as exc:
        raise http_exception_from_app_error(exc)
