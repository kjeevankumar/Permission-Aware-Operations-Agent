"""Pydantic schemas for authentication and tokens."""

from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Credentials required for user authentication."""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """Bearer access token payload returned upon successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Decoded token claims."""

    sub: Optional[str] = None
    hospital_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(extra="ignore")
