"""Hospital tenant database model."""

import uuid
from typing import List, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.inventory import InventoryItem
    from app.database.models.bill import Bill
    from app.database.models.audit import AuditLog
    from app.database.models.pending_operation import PendingOperation


class Hospital(Base, TimestampMixin):
    """Hospital tenant entity representing an isolated healthcare facility."""

    __tablename__ = "hospitals"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        sa.String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    city: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    state: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )
    bills: Mapped[List["Bill"]] = relationship(
        "Bill",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )
    pending_operations: Mapped[List["PendingOperation"]] = relationship(
        "PendingOperation",
        back_populates="hospital",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Hospital(id={self.id}, code='{self.code}', city='{self.city}')>"
