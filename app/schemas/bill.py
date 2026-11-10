"""Pydantic schemas for billing operations."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BillRead(BaseModel):
    """Safe schema for returning hospital patient bills."""

    id: uuid.UUID
    hospital_id: uuid.UUID
    bill_number: str
    patient_name: str
    patient_mrn: str
    total_amount: Decimal
    discount_pct: Decimal
    final_amount: Decimal
    status: str
    doctor_id: Optional[uuid.UUID] = None
    created_by_user_id: uuid.UUID
    notes: Optional[str] = None
    bill_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillDiscountRequest(BaseModel):
    """Payload for applying a discount to a bill."""

    discount_pct: Decimal = Field(..., ge=0, le=100, description="Discount percentage between 0 and 100")
    reason: Optional[str] = Field(None, max_length=255, description="Audit reason for discount")


class BillStatusUpdateRequest(BaseModel):
    """Payload for updating a bill status (e.g. pending -> paid)."""

    status: str = Field(..., description="Target status: pending, paid, cancelled, disputed")
    notes: Optional[str] = Field(None, max_length=500)
