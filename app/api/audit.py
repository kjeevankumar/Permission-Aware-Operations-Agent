"""Audit logs query API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
import sqlalchemy as sa
from app.database.connection import get_db
from app.core.dependencies import get_current_user_context, require_permission
from app.security.authentication import UserContext
from app.security.tenant import scope_query_to_tenant
from app.database.models.audit import AuditLog
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit", tags=["Compliance & Audit Logs"])


@router.get("", response_model=List[AuditLogRead])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    context: UserContext = Depends(require_permission("audit.read")),
    db: Session = Depends(get_db),
) -> List[AuditLogRead]:
    """
    List immutable audit log records strictly scoped to the user's hospital tenant.
    Requires audit.read permission.
    """
    stmt = sa.select(AuditLog)
    stmt = scope_query_to_tenant(stmt, AuditLog, context.hospital_id)
    stmt = stmt.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())
