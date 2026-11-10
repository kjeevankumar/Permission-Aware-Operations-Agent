"""Audit logging service providing immutable compliance records."""

import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models.audit import AuditLog


def log_audit_event(
    db: Session,
    hospital_id: uuid.UUID,
    user_id: Optional[uuid.UUID],
    action: str,
    resource_type: str,
    status: str,
    resource_id: Optional[str] = None,
    before_state: Optional[Dict[str, Any]] = None,
    after_state: Optional[Dict[str, Any]] = None,
    metadata_info: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """
    Write an immutable audit record to the database.
    Catches and logs security actions, updates, discounts, and preview confirmations.
    """
    log_entry = AuditLog(
        hospital_id=hospital_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        before_state=before_state,
        after_state=after_state,
        metadata_info=metadata_info or {},
        ip_address=ip_address,
    )
    db.add(log_entry)
    db.flush()
    return log_entry
