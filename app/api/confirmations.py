"""API endpoints for previewing, listing, confirming, and rejecting staged operations."""

import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.pending_operation import PendingOperation
from app.core.dependencies import get_current_user_context, require_permission
from app.security.authentication import UserContext
from app.security.tenant import scope_query_to_tenant
from app.schemas.confirmation import (
    PreviewOperationRequest,
    PendingOperationRead,
    ConfirmOperationRequest,
)
from app.services.preview import create_operation_preview
from app.services.confirmation import confirm_pending_operation, reject_pending_operation
from app.core.exceptions import AppException, http_exception_from_app_error

router = APIRouter(prefix="/confirmations", tags=["Confirmations & Previews"])


@router.post("/preview", response_model=PendingOperationRead, status_code=status.HTTP_201_CREATED)
def stage_preview_operation(
    request: PreviewOperationRequest,
    context: UserContext = Depends(require_permission("operations.preview")),
    db: Session = Depends(get_db),
) -> PendingOperationRead:
    """
    Stage an operation preview: calculates before/after diffs and checks policy constraints.
    Returns preview diff with an expiration TTL.
    """
    try:
        pending_op = create_operation_preview(
            db=db,
            context=context,
            operation_type=request.operation_type,
            target_resource=request.target_resource,
            filter_criteria=request.filter_criteria,
            proposed_changes=request.proposed_changes,
        )
        db.commit()
        db.refresh(pending_op)
        return pending_op
    except AppException as exc:
        db.rollback()
        raise http_exception_from_app_error(exc)


@router.get("/pending", response_model=List[PendingOperationRead])
def list_pending_operations(
    context: UserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
) -> List[PendingOperationRead]:
    """List all staged pending operations awaiting confirmation in this hospital."""
    stmt = sa.select(PendingOperation).where(PendingOperation.status == "pending")
    stmt = scope_query_to_tenant(stmt, PendingOperation, context.hospital_id)
    stmt = stmt.order_by(PendingOperation.created_at.desc())
    results = db.execute(stmt).scalars().all()
    return list(results)


@router.post("/{operation_id}/confirm")
def confirm_operation(
    operation_id: uuid.UUID,
    request: ConfirmOperationRequest = ConfirmOperationRequest(),
    context: UserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Confirm and atomically execute a staged pending operation.
    Guarantees strict tenant checks and records an audit log.
    """
    try:
        result = confirm_pending_operation(
            db=db,
            context=context,
            operation_id=operation_id,
            reason=request.reason,
        )
        return result
    except AppException as exc:
        raise http_exception_from_app_error(exc)


@router.post("/{operation_id}/reject", response_model=PendingOperationRead)
def reject_operation(
    operation_id: uuid.UUID,
    request: ConfirmOperationRequest = ConfirmOperationRequest(),
    context: UserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
) -> PendingOperationRead:
    """Explicitly reject a staged operation without modifying target records."""
    try:
        op = reject_pending_operation(
            db=db,
            context=context,
            operation_id=operation_id,
            reason=request.reason,
        )
        return op
    except AppException as exc:
        raise http_exception_from_app_error(exc)
