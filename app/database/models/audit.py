"""Audit log database model for comprehensive compliance and change tracking."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.hospital import Hospital
    from app.database.models.user import User


class AuditLog(Base, TenantMixin):
    """Immutable audit trail of all security-sensitive actions and operations."""

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        sa.String(100),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        sa.String(50),
        nullable=False,
        index=True,
        comment="Operation status: SUCCESS, DENIED, FAILED",
    )
    before_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        sa.JSON,
        nullable=True,
        comment="Resource state snapshot before modification",
    )
    after_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        sa.JSON,
        nullable=True,
        comment="Resource state snapshot after modification",
    )
    metadata_info: Mapped[Dict[str, Any]] = mapped_column(
        sa.JSON,
        default=dict,
        nullable=False,
        server_default="{}",
        comment="Operational context (e.g. constraints applied, IP, user-agent)",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        sa.String(45),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=sa.func.now(),
        index=True,
    )

    # Relationships
    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="audit_logs",
    )
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="audit_logs",
    )

    __table_args__ = (
        sa.Index("idx_audit_tenant_action", "hospital_id", "action"),
        sa.Index("idx_audit_tenant_resource", "hospital_id", "resource_type"),
        sa.Index("idx_audit_tenant_created", "hospital_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}', "
            f"status='{self.status}')>"
        )
