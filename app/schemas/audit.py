"""Pydantic schemas for audit logging records."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    """Schema for querying immutable audit log entries."""

    id: uuid.UUID
    hospital_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    status: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    metadata_info: Dict[str, Any]
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
