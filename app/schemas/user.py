"""Pydantic schemas for users, roles, and permissions."""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RoleRead(BaseModel):
    """Schema representing an assigned role."""

    id: uuid.UUID
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PermissionRead(BaseModel):
    """Schema representing a system permission."""

    id: uuid.UUID
    code: str
    description: Optional[str] = None
    category: str

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    """Safe public user representation (never exposes hashed_password)."""

    id: uuid.UUID
    hospital_id: uuid.UUID
    username: str
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    full_name: str
    is_active: bool
    roles: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserContextResponse(BaseModel):
    """Comprehensive verified user context returned by /auth/me."""

    user_id: uuid.UUID
    hospital_id: uuid.UUID
    username: str
    email: str
    full_name: str
    active_roles: List[str]
    permissions: Dict[str, Dict[str, Any]]
    account_status: str
