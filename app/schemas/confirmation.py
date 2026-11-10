"""Pydantic schemas for previewing and confirming staged operations."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class PreviewOperationRequest(BaseModel):
    """Payload to request a dry-run preview and diff generation for an operation."""

    operation_type: str = Field(..., description="E.g. inventory.update, bills.discount, inventory.delete")
    target_resource: str = Field(..., description="E.g. inventory_items, bills")
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    proposed_changes: Dict[str, Any] = Field(default_factory=dict)


class PendingOperationRead(BaseModel):
    """Schema for returning staged pending operations awaiting confirmation."""

    id: uuid.UUID
    hospital_id: uuid.UUID
    user_id: uuid.UUID
    operation_type: str
    target_resource: str
    filter_criteria: Dict[str, Any]
    proposed_changes: Dict[str, Any]
    impacted_row_count: int
    preview_diff: Dict[str, Any]
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConfirmOperationRequest(BaseModel):
    """Request payload to confirm or reject a staged pending operation."""

    reason: Optional[str] = Field(None, max_length=255, description="Confirmation or rejection justification")
