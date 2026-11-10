"""Role-specific policy and operational constraint validators."""

import uuid
from decimal import Decimal
from typing import Optional
from app.security.authentication import UserContext
from app.security.permissions import StandardPermission
from app.core.exceptions import ConstraintViolationError, PermissionDeniedError


def validate_inventory_update_constraints(
    context: UserContext,
    affected_row_count: int,
) -> None:
    """
    Validate inventory update constraints.
    E.g. Pharmacist role constraint: {"max_rows": 500}
    """
    if not context.has_permission(StandardPermission.INVENTORY_UPDATE.value):
        raise PermissionDeniedError("User lacks inventory.update permission.")

    max_rows = context.get_constraint(StandardPermission.INVENTORY_UPDATE.value, "max_rows")
    if max_rows is not None and affected_row_count > int(max_rows):
        raise ConstraintViolationError(
            f"Operation impacts {affected_row_count} rows, exceeding your permitted maximum of {max_rows} rows.",
            details={"requested_rows": affected_row_count, "max_rows": max_rows},
        )


def validate_bill_discount_constraints(
    context: UserContext,
    proposed_discount_pct: Decimal,
) -> None:
    """
    Validate discount percentage constraints.
    E.g. Billing Manager: {"max_discount_pct": 10}, Admin: {"max_discount_pct": 100}
    """
    if not context.has_permission(StandardPermission.BILLS_DISCOUNT.value):
        raise PermissionDeniedError("User lacks bills.discount permission.")

    max_pct = context.get_constraint(StandardPermission.BILLS_DISCOUNT.value, "max_discount_pct")
    if max_pct is not None:
        max_pct_decimal = Decimal(str(max_pct))
        if proposed_discount_pct > max_pct_decimal:
            raise ConstraintViolationError(
                f"Proposed discount of {proposed_discount_pct}% exceeds your maximum permitted discount of {max_pct_decimal}%.",
                details={
                    "proposed_discount_pct": float(proposed_discount_pct),
                    "max_discount_pct": float(max_pct_decimal),
                },
            )


def check_bill_read_scope(
    context: UserContext,
    bill_creator_id: uuid.UUID,
) -> bool:
    """
    Evaluate record-level visibility scope.
    E.g. Front Desk: {"scope": "own_records"}
    Returns True if user has access to view this bill record.
    """
    if not context.has_permission(StandardPermission.BILLS_READ.value):
        return False

    scope = context.get_constraint(StandardPermission.BILLS_READ.value, "scope")
    if scope == "own_records":
        return context.user_id == bill_creator_id

    # If no scope restriction, default to tenant-wide visibility
    return True
