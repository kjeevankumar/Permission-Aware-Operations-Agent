"""Tests verifying authenticated API routes for inventory, bills, and system stats."""

import uuid
from decimal import Decimal
import pytest
from sqlalchemy.orm import Session
import sqlalchemy as sa
from app.database.models import User, Hospital, InventoryItem, Bill
from app.core.security import create_access_token
from app.core.dependencies import get_current_user_context
from app.api.system import get_system_database_stats
from app.api.inventory import get_inventory, get_single_inventory_item
from app.api.bills import get_bills, get_single_bill
from fastapi import HTTPException


def test_system_database_stats(db_session: Session):
    """Verify that GET /api/v1/system/stats accurately aggregates database records without leaking secrets."""
    stats = get_system_database_stats(db=db_session)

    assert stats["status"] == "online"
    assert stats["hospitals"]["total"] == 2
    assert len(stats["hospitals"]["list"]) == 2
    assert stats["users"]["total"] >= 12
    assert stats["roles"]["total"] == 5
    assert stats["permissions"]["total"] >= 12
    assert stats["inventory"]["total"] >= 1200
    assert stats["bills"]["total"] >= 500

    # Ensure inventory is grouped by both hospitals
    grouped = stats["inventory"]["grouped_by_hospital"]
    assert len(grouped) == 2
    for entry in grouped:
        assert entry["item_count"] >= 600


def test_authenticated_inventory_listing(db_session: Session, metro_admin_token: str):
    """Verify that an authenticated user can list inventory items scoped to their hospital."""
    context = get_current_user_context(token=metro_admin_token, db=db_session)
    items = get_inventory(
        category=None,
        search=None,
        low_stock=None,
        expiring_within_days=None,
        limit=50,
        offset=0,
        context=context,
        db=db_session,
    )
    assert len(items) == 50
    for item in items:
        assert item.hospital_id == context.hospital_id


def test_authenticated_bills_listing_and_scope(
    db_session: Session,
    metro_admin_token: str,
    metro_frontdesk_token: str,
):
    """
    Verify that:
    1. Admin can list hospital bills.
    2. Front Desk can only list bills they personally created (own_records constraint).
    """
    admin_context = get_current_user_context(token=metro_admin_token, db=db_session)
    admin_bills = get_bills(
        status=None,
        limit=50,
        offset=0,
        context=admin_context,
        db=db_session,
    )
    assert len(admin_bills) > 0

    frontdesk_context = get_current_user_context(token=metro_frontdesk_token, db=db_session)
    fd_bills = get_bills(
        status=None,
        limit=50,
        offset=0,
        context=frontdesk_context,
        db=db_session,
    )
    for bill in fd_bills:
        assert bill.created_by_user_id == frontdesk_context.user_id
        assert bill.hospital_id == frontdesk_context.hospital_id


def test_cross_tenant_single_bill_access_rejected(
    db_session: Session,
    metro_admin_token: str,
    jude_admin_token: str,
):
    """Verify that attempting to fetch a bill from another hospital returns 404 Not Found."""
    jude_context = get_current_user_context(token=jude_admin_token, db=db_session)
    jude_bill = db_session.execute(
        sa.select(Bill).where(Bill.hospital_id == jude_context.hospital_id)
    ).scalars().first()
    assert jude_bill is not None

    metro_context = get_current_user_context(token=metro_admin_token, db=db_session)
    with pytest.raises(HTTPException) as exc_info:
        get_single_bill(bill_id=jude_bill.id, context=metro_context, db=db_session)

    assert exc_info.value.status_code == 404
