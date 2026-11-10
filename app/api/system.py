"""System and database verification statistics endpoint."""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sqlalchemy as sa
from app.database.connection import get_db
from app.database.models import (
    Hospital,
    User,
    Role,
    Permission,
    InventoryItem,
    Bill,
    AuditLog,
)

router = APIRouter(prefix="/system", tags=["System & Verification"])


@router.get("/stats", response_model=Dict[str, Any])
def get_system_database_stats(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Development & verification statistics endpoint.
    Reports table row counts and inventory counts grouped by hospital.
    Excludes any patient or sensitive operational details.
    """
    # 1. Total counts
    hospital_count = db.execute(sa.select(sa.func.count(Hospital.id))).scalar() or 0
    user_count = db.execute(sa.select(sa.func.count(User.id))).scalar() or 0
    role_count = db.execute(sa.select(sa.func.count(Role.id))).scalar() or 0
    permission_count = db.execute(sa.select(sa.func.count(Permission.id))).scalar() or 0
    total_inventory = db.execute(sa.select(sa.func.count(InventoryItem.id))).scalar() or 0
    bill_count = db.execute(sa.select(sa.func.count(Bill.id))).scalar() or 0
    audit_count = db.execute(sa.select(sa.func.count(AuditLog.id))).scalar() or 0

    # 2. Inventory grouped by hospital
    inv_by_hosp_query = (
        sa.select(Hospital.name, Hospital.code, sa.func.count(InventoryItem.id))
        .join(InventoryItem, InventoryItem.hospital_id == Hospital.id)
        .group_by(Hospital.id, Hospital.name, Hospital.code)
        .order_by(Hospital.name)
    )
    inv_by_hosp = [
        {"hospital_name": name, "code": code, "item_count": count}
        for name, code, count in db.execute(inv_by_hosp_query).all()
    ]

    # 3. Hospitals list
    hospitals_query = sa.select(Hospital.id, Hospital.name, Hospital.code, Hospital.city).order_by(Hospital.name)
    hospitals = [
        {"id": str(h_id), "name": name, "code": code, "city": city}
        for h_id, name, code, city in db.execute(hospitals_query).all()
    ]

    return {
        "status": "online",
        "hospitals": {
            "total": hospital_count,
            "list": hospitals,
        },
        "users": {
            "total": user_count,
        },
        "roles": {
            "total": role_count,
        },
        "permissions": {
            "total": permission_count,
        },
        "inventory": {
            "total": total_inventory,
            "grouped_by_hospital": inv_by_hosp,
        },
        "bills": {
            "total": bill_count,
        },
        "audit_log": {
            "total": audit_count,
        },
    }
