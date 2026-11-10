"""Chat endpoint interface for Phase 2 natural-language interaction."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.core.dependencies import get_current_user_context
from app.security.authentication import UserContext

router = APIRouter(prefix="/chat", tags=["Agent Chat (Phase 2)"])


class ChatMessageRequest(BaseModel):
    """User prompt sent to the natural language agent."""

    message: str = Field(..., min_length=1, max_length=2000, description="Natural language operation instruction")


class ChatMessageResponse(BaseModel):
    """Agent response structure."""

    response: str
    phase: str = "Phase 1: Foundation Active"
    status: str


@router.post("", response_model=ChatMessageResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def handle_chat_message(
    payload: ChatMessageRequest,
    context: UserContext = Depends(get_current_user_context),
) -> Dict[str, Any]:
    """
    Phase 2 natural-language agent interface endpoint.
    Phase 1 delivers the secure database, RBAC, tenant isolation, and confirmation pipeline.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "message": "Natural-language LLM execution is scheduled for Phase 2.",
            "status": "foundation_ready",
            "active_user": context.username,
            "hospital_id": str(context.hospital_id),
            "assigned_roles": context.active_roles,
        },
    )
