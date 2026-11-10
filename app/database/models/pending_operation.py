"""Pending operations model for staged previews requiring explicit confirmation."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.hospital import Hospital
    from app.database.models.user import User


class PendingOperation(Base, TenantMixin):
    """Staged operation record holding preview diffs and state awaiting explicit human confirmation."""

    __tablename__ = "pending_operations"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who requested the previewed operation",
    )
    operation_type: Mapped[str] = mapped_column(
        sa.String(50),
        nullable=False,
        index=True,
        comment="E.g. inventory.update, bills.discount, inventory.delete",
    )
    target_resource: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
        comment="E.g. inventory_items, bills",
    )
    filter_criteria: Mapped[Dict[str, Any]] = mapped_column(
        sa.JSON,
        default=dict,
        nullable=False,
        server_default="{}",
        comment="Filter parameters used to select target rows",
    )
    proposed_changes: Mapped[Dict[str, Any]] = mapped_column(
        sa.JSON,
        default=dict,
        nullable=False,
        server_default="{}",
        comment="Changes proposed to be applied",
    )
    impacted_row_count: Mapped[int] = mapped_column(
        sa.Integer,
        default=0,
        nullable=False,
        comment="Number of records affected by this operation",
    )
    preview_diff: Mapped[Dict[str, Any]] = mapped_column(
        sa.JSON,
        default=dict,
        nullable=False,
        server_default="{}",
        comment="Detailed before/after diff preview of affected rows",
    )
    status: Mapped[str] = mapped_column(
        sa.String(50),
        default="pending",
        nullable=False,
        index=True,
        comment="Status: pending, confirmed, rejected, expired",
    )
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    confirmed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
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
        back_populates="pending_operations",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="pending_operations",
    )
    confirmed_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[confirmed_by_user_id],
    )

    __table_args__ = (
        sa.Index("idx_pending_tenant_status", "hospital_id", "status"),
        sa.Index("idx_pending_tenant_expiry", "hospital_id", "expires_at"),
    )

    def is_expired(self) -> bool:
        """Check if pending operation has expired."""
        now = datetime.now(timezone.utc)
        return now > self.expires_at

    def __repr__(self) -> str:
        return (
            f"<PendingOperation(id={self.id}, type='{self.operation_type}', status='{self.status}', "
            f"impact={self.impacted_row_count})>"
        )
