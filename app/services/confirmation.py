"""Service managing confirmation and rejection of staged pending operations."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models.pending_operation import PendingOperation
from app.security.authentication import UserContext
from app.security.tenant import verify_tenant_boundary
from app.security.permissions import StandardPermission
from app.services.execution import execute_operation
from app.services.audit import log_audit_event
from app.core.exceptions import (
    EntityNotFoundError,
    OperationExpiredError,
    PermissionDeniedError,
    AppException,
)


def confirm_pending_operation(
    db: Session,
    context: UserContext,
    operation_id: uuid.UUID,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Confirm and atomically execute a staged pending operation:
    1. Verify operation exists and belongs to the user's hospital tenant.
    2. Check expiration TTL.
    3. Ensure user possesses confirmation permission and target operation permission.
    4. Execute database changes atomically and record audit trail.
    5. Mark operation as confirmed.
    """
    stmt = sa.select(PendingOperation).where(PendingOperation.id == operation_id)
    pending_op = db.execute(stmt).scalar_one_or_none()

    if not pending_op:
        raise EntityNotFoundError(f"Pending operation '{operation_id}' not found.")

    # Strict tenant isolation
    verify_tenant_boundary(pending_op, context.hospital_id)

    if pending_op.status != "pending":
        raise AppException(f"Operation cannot be confirmed; current status is '{pending_op.status}'.")

    if pending_op.is_expired():
        pending_op.status = "expired"
        db.commit()
        raise OperationExpiredError("Pending operation has expired. Please re-run the preview.")

    # Permission check: require either operations.confirm or the operation permission
    can_confirm = (
        context.has_permission(StandardPermission.OPERATIONS_CONFIRM.value)
        or context.has_permission(pending_op.operation_type)
    )
    if not can_confirm:
        raise PermissionDeniedError(
            f"User lacks permission to confirm operation '{pending_op.operation_type}'."
        )

    # Execute atomically
    execution_result = execute_operation(db, context, pending_op)

    # Update pending operation state
    pending_op.status = "confirmed"
    pending_op.confirmed_at = datetime.now(timezone.utc)
    pending_op.confirmed_by_user_id = context.user_id

    log_audit_event(
        db=db,
        hospital_id=context.hospital_id,
        user_id=context.user_id,
        action="operation.confirm",
        resource_type="pending_operations",
        resource_id=str(pending_op.id),
        status="SUCCESS",
        metadata_info={"reason": reason, "execution_result": execution_result},
    )

    db.commit()
    return execution_result


def reject_pending_operation(
    db: Session,
    context: UserContext,
    operation_id: uuid.UUID,
    reason: Optional[str] = None,
) -> PendingOperation:
    """
    Explicitly reject a staged pending operation without applying changes.
    """
    stmt = sa.select(PendingOperation).where(PendingOperation.id == operation_id)
    pending_op = db.execute(stmt).scalar_one_or_none()

    if not pending_op:
        raise EntityNotFoundError(f"Pending operation '{operation_id}' not found.")

    verify_tenant_boundary(pending_op, context.hospital_id)

    if pending_op.status != "pending":
        raise AppException(f"Operation cannot be rejected; current status is '{pending_op.status}'.")

    pending_op.status = "rejected"

    log_audit_event(
        db=db,
        hospital_id=context.hospital_id,
        user_id=context.user_id,
        action="operation.reject",
        resource_type="pending_operations",
        resource_id=str(pending_op.id),
        status="SUCCESS",
        metadata_info={"reason": reason},
    )

    db.commit()
    return pending_op
