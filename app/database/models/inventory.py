"""Inventory item database model for hospital pharmacy and medical supplies."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.database.models.hospital import Hospital


class InventoryItem(Base, TimestampMixin, TenantMixin):
    """Inventory item entity representing pharmaceuticals and clinical supplies."""

    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    sku: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    batch_number: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(
        sa.Integer,
        default=0,
        nullable=False,
    )
    reorder_level: Mapped[int] = mapped_column(
        sa.Integer,
        default=10,
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=10, scale=2),
        nullable=False,
    )
    expiry_date: Mapped[date] = mapped_column(
        sa.Date,
        nullable=False,
        index=True,
    )
    location: Mapped[Optional[str]] = mapped_column(
        sa.String(100),
        nullable=True,
    )

    # Relationships
    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="inventory_items",
    )

    __table_args__ = (
        sa.Index("idx_inventory_tenant_sku", "hospital_id", "sku"),
        sa.Index("idx_inventory_tenant_category", "hospital_id", "category"),
        sa.Index("idx_inventory_tenant_expiry", "hospital_id", "expiry_date"),
        sa.Index("idx_inventory_tenant_quantity", "hospital_id", "quantity"),
        sa.CheckConstraint("quantity >= 0", name="chk_inventory_quantity_non_negative"),
        sa.CheckConstraint("unit_price >= 0", name="chk_inventory_unit_price_non_negative"),
    )

    def __repr__(self) -> str:
        return (
            f"<InventoryItem(id={self.id}, sku='{self.sku}', name='{self.name}', "
            f"batch='{self.batch_number}', qty={self.quantity})>"
        )
