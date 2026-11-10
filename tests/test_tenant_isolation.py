"""Tests verifying strict hospital tenant isolation, role constraints, and permission overrides."""

from decimal import Decimal
import uuid
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.models import Hospital, User, InventoryItem, Bill, PendingOperation
from app.security.authentication import resolve_user_context
from app.operations.inventory import list_inventory_items, get_inventory_item
from app.operations.bills import list_bills, get_bill
from app.operations.users import set_user_permission_override
from app.services.preview import create_operation_preview
from app.services.confirmation import confirm_pending_operation
from app.core.exceptions import (
    EntityNotFoundError,
    PermissionDeniedError,
    ConstraintViolationError,
    TenantAccessViolationError,
)


def test_hospital_a_cannot_see_hospital_b_inventory(db_session: Session):
    """Verify that a user from Hospital A (Metro) cannot list or access inventory belonging to Hospital B (St. Jude)."""
    metro_user = db_session.execute(
        sa.select(User).where(User.username == "pharma.metro")
    ).scalar_one()
    jude_user = db_session.execute(
        sa.select(User).where(User.username == "pharma.jude")
    ).scalar_one()

    metro_context = resolve_user_context(db_session, metro_user.id)
    jude_context = resolve_user_context(db_session, jude_user.id)

    assert metro_context.hospital_id != jude_context.hospital_id

    # List inventory for Metro user
    metro_items = list_inventory_items(db_session, metro_context, limit=1000)
    assert len(metro_items) >= 600

    # Ensure every single item retrieved belongs exclusively to Metro Health
    for item in metro_items:
        assert item.hospital_id == metro_context.hospital_id
        assert item.hospital_id != jude_context.hospital_id

    # Retrieve an item belonging to St. Jude
    jude_item = db_session.execute(
        sa.select(InventoryItem).where(InventoryItem.hospital_id == jude_context.hospital_id)
    ).scalars().first()
    assert jude_item is not None

    # Metro user attempting to access St. Jude's item must raise EntityNotFoundError
    with pytest.raises(EntityNotFoundError):
        get_inventory_item(db_session, metro_context, jude_item.id)


def test_hospital_a_cannot_see_hospital_b_bills(db_session: Session):
    """Verify that a user from Hospital A cannot query or view bills from Hospital B."""
    metro_billing = db_session.execute(
        sa.select(User).where(User.username == "billing.metro")
    ).scalar_one()
    jude_billing = db_session.execute(
        sa.select(User).where(User.username == "billing.jude")
    ).scalar_one()

    metro_context = resolve_user_context(db_session, metro_billing.id)
    jude_context = resolve_user_context(db_session, jude_billing.id)

    metro_bills = list_bills(db_session, metro_context, limit=1000)
    assert len(metro_bills) >= 200

    for bill in metro_bills:
        assert bill.hospital_id == metro_context.hospital_id
        assert bill.hospital_id != jude_context.hospital_id

    jude_bill = db_session.execute(
        sa.select(Bill).where(Bill.hospital_id == jude_context.hospital_id)
    ).scalars().first()

    with pytest.raises(EntityNotFoundError):
        get_bill(db_session, metro_context, jude_bill.id)


def test_cross_tenant_operation_confirmation_blocked(db_session: Session):
    """Verify that a user from Hospital A cannot confirm an operation staged in Hospital B."""
    metro_admin = db_session.execute(
        sa.select(User).where(User.username == "admin.metro")
    ).scalar_one()
    jude_admin = db_session.execute(
        sa.select(User).where(User.username == "admin.jude")
    ).scalar_one()

    metro_context = resolve_user_context(db_session, metro_admin.id)
    jude_context = resolve_user_context(db_session, jude_admin.id)

    # St. Jude stages an operation preview
    jude_pending_op = create_operation_preview(
        db=db_session,
        context=jude_context,
        operation_type="inventory.update",
        target_resource="inventory_items",
        filter_criteria={"category": "Antibiotics"},
        proposed_changes={"unit_price": Decimal("25.00")},
    )
    db_session.flush()

    # Metro Admin attempts to confirm St. Jude's operation
    with pytest.raises(TenantAccessViolationError):
        confirm_pending_operation(db_session, metro_context, jude_pending_op.id)


def test_pharmacist_inventory_update_constraint_max_rows(db_session: Session):
    """Verify that Pharmacist max_rows constraint (500) blocks updates impacting more than 500 rows."""
    metro_pharma = db_session.execute(
        sa.select(User).where(User.username == "pharma.metro")
    ).scalar_one()
    pharma_context = resolve_user_context(db_session, metro_pharma.id)

    # Metro has 620 inventory items. An empty filter impacts all 620 items, exceeding 500 limit.
    with pytest.raises(ConstraintViolationError) as exc_info:
        create_operation_preview(
            db=db_session,
            context=pharma_context,
            operation_type="inventory.update",
            target_resource="inventory_items",
            filter_criteria={},  # Targets all items
            proposed_changes={"location": "Central Depot"},
        )
    assert "exceeding your permitted maximum of 500 rows" in str(exc_info.value)


def test_billing_manager_discount_constraint(db_session: Session):
    """Verify that Billing Manager cannot apply discount > 10%, while Admin can apply up to 100%."""
    metro_billing = db_session.execute(
        sa.select(User).where(User.username == "billing.metro")
    ).scalar_one()
    metro_admin = db_session.execute(
        sa.select(User).where(User.username == "admin.metro")
    ).scalar_one()

    billing_context = resolve_user_context(db_session, metro_billing.id)
    admin_context = resolve_user_context(db_session, metro_admin.id)

    bill = db_session.execute(
        sa.select(Bill).where(Bill.hospital_id == billing_context.hospital_id)
    ).scalars().first()

    # Billing Manager attempts 15% discount -> Should fail constraint
    with pytest.raises(ConstraintViolationError) as exc_info:
        create_operation_preview(
            db=db_session,
            context=billing_context,
            operation_type="bills.discount",
            target_resource="bills",
            filter_criteria={"id": bill.id},
            proposed_changes={"discount_pct": Decimal("15.00")},
        )
    assert "exceeds your maximum permitted discount of 10" in str(exc_info.value)

    # Billing Manager attempts 10% discount -> Permitted
    preview_valid = create_operation_preview(
        db=db_session,
        context=billing_context,
        operation_type="bills.discount",
        target_resource="bills",
        filter_criteria={"id": bill.id},
        proposed_changes={"discount_pct": Decimal("10.00")},
    )
    assert preview_valid.impacted_row_count == 1

    # Admin attempts 25% discount -> Permitted (Admin max is 100%)
    preview_admin = create_operation_preview(
        db=db_session,
        context=admin_context,
        operation_type="bills.discount",
        target_resource="bills",
        filter_criteria={"id": bill.id},
        proposed_changes={"discount_pct": Decimal("25.00")},
    )
    assert preview_admin.impacted_row_count == 1


def test_front_desk_scope_own_records(db_session: Session):
    """Verify that Front Desk staff can only view bills that they created."""
    frontdesk_user = db_session.execute(
        sa.select(User).where(User.username == "frontdesk.metro")
    ).scalar_one()
    frontdesk_context = resolve_user_context(db_session, frontdesk_user.id)

    bills = list_bills(db_session, frontdesk_context)
    for bill in bills:
        assert bill.created_by_user_id == frontdesk_user.id


def test_user_permission_override_isolated_to_individual(db_session: Session):
    """
    Verify that overriding a permission for one user (e.g. revoking inventory.update from pharma.metro)
    does not affect other users sharing the same Pharmacist role (e.g. ravi.kumar).
    """
    pharma_metro = db_session.execute(
        sa.select(User).where(User.username == "pharma.metro")
    ).scalar_one()
    ravi_kumar = db_session.execute(
        sa.select(User).where(User.username == "ravi.kumar")
    ).scalar_one()
    admin_metro = db_session.execute(
        sa.select(User).where(User.username == "admin.metro")
    ).scalar_one()

    admin_context = resolve_user_context(db_session, admin_metro.id)

    # Revoke inventory.update specifically from pharma_metro
    set_user_permission_override(
        db=db_session,
        context=admin_context,
        target_user_id=pharma_metro.id,
        permission_code="inventory.update",
        is_granted=False,
        reason="Suspended from inventory modification pending audit review",
    )

    # Resolve context for pharma_metro: inventory.update must be absent
    pharma_context = resolve_user_context(db_session, pharma_metro.id)
    assert not pharma_context.has_permission("inventory.update")

    # Resolve context for ravi_kumar: inventory.update must STILL be present!
    ravi_context = resolve_user_context(db_session, ravi_kumar.id)
    assert ravi_context.has_permission("inventory.update")
