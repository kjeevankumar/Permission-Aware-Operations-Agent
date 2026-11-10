"""Pydantic schemas for inventory operations."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InventoryItemRead(BaseModel):
    """Schema for returning pharmacy and inventory item details."""

    id: uuid.UUID
    hospital_id: uuid.UUID
    sku: str
    name: str
    category: str
    batch_number: str
    quantity: int
    reorder_level: int
    unit_price: Decimal
    expiry_date: date
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InventoryUpdate(BaseModel):
    """Fields permissible for inventory update operations."""

    quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    location: Optional[str] = None


class InventoryFilter(BaseModel):
    """Filter criteria for inventory queries."""

    category: Optional[str] = None
    search: Optional[str] = None
    low_stock: Optional[bool] = None
    expiring_within_days: Optional[int] = Field(None, ge=1)
