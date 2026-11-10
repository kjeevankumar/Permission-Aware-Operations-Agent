"""Hospital billing database model."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.database.models.hospital import Hospital
    from app.database.models.user import User


class Bill(Base, TimestampMixin, TenantMixin):
    """Hospital patient billing entity representing invoice records."""

    __tablename__ = "bills"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    bill_number: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    patient_name: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
        index=True,
    )
    patient_mrn: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
        comment="Medical Record Number for patient tracking",
    )
    total_amount: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=12, scale=2),
        nullable=False,
    )
    discount_pct: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=5, scale=2),
        default=Decimal("0.00"),
        nullable=False,
    )
    final_amount: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=12, scale=2),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        sa.String(50),
        default="draft",
        nullable=False,
        index=True,
        comment="Bill status: draft, pending, paid, cancelled, disputed",
    )
    doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        sa.Text,
        nullable=True,
    )
    bill_date: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="bills",
    )
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="bills_created",
    )
    doctor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[doctor_id],
        back_populates="bills_as_doctor",
    )

    __table_args__ = (
        sa.Index("idx_bills_tenant_number", "hospital_id", "bill_number"),
        sa.Index("idx_bills_tenant_status", "hospital_id", "status"),
        sa.Index("idx_bills_tenant_date", "hospital_id", "bill_date"),
        sa.Index("idx_bills_tenant_mrn", "hospital_id", "patient_mrn"),
        sa.Index("idx_bills_tenant_creator", "hospital_id", "created_by_user_id"),
        sa.CheckConstraint("total_amount >= 0", name="chk_bills_total_non_negative"),
        sa.CheckConstraint(
            "discount_pct >= 0 AND discount_pct <= 100",
            name="chk_bills_discount_range",
        ),
        sa.CheckConstraint("final_amount >= 0", name="chk_bills_final_non_negative"),
    )

    def __repr__(self) -> str:
        return (
            f"<Bill(id={self.id}, number='{self.bill_number}', patient='{self.patient_name}', "
            f"total={self.total_amount}, final={self.final_amount}, status='{self.status}')>"
        )
