"""API router configuration package."""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.confirmations import router as confirmations_router
from app.api.inventory import router as inventory_router
from app.api.bills import router as bills_router
from app.api.audit import router as audit_router
from app.api.system import router as system_router
from app.api.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(inventory_router)
api_router.include_router(bills_router)
api_router.include_router(confirmations_router)
api_router.include_router(audit_router)
api_router.include_router(system_router)
api_router.include_router(chat_router)

__all__ = ["api_router"]
