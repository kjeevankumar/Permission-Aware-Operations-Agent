"""SQLAlchemy declarative base and common model mixins."""

import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return current UTC timestamp with timezone."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


class TimestampMixin:
    """Mixin adding created_at and updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
        server_default=sa.func.now(),
    )


class TenantMixin:
    """Mixin adding hospital_id foreign key for multi-tenant isolation."""

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("hospitals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
