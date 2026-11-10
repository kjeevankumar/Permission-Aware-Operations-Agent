"""User, UserRole, and UserPermissionOverride models."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.database.models.hospital import Hospital
    from app.database.models.role import Role
    from app.database.models.permission import Permission
    from app.database.models.bill import Bill
    from app.database.models.pending_operation import PendingOperation
    from app.database.models.audit import AuditLog


class User(Base, TimestampMixin, TenantMixin):
    """User account entity belonging to exactly one hospital tenant."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        sa.String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        sa.String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="users",
    )
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    permission_overrides: Mapped[List["UserPermissionOverride"]] = relationship(
        "UserPermissionOverride",
        foreign_keys="UserPermissionOverride.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bills_created: Mapped[List["Bill"]] = relationship(
        "Bill",
        foreign_keys="Bill.created_by_user_id",
        back_populates="creator",
    )
    bills_as_doctor: Mapped[List["Bill"]] = relationship(
        "Bill",
        foreign_keys="Bill.doctor_id",
        back_populates="doctor",
    )
    pending_operations: Mapped[List["PendingOperation"]] = relationship(
        "PendingOperation",
        foreign_keys="PendingOperation.user_id",
        back_populates="user",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        foreign_keys="AuditLog.user_id",
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', hospital_id={self.hospital_id})>"


class UserRole(Base):
    """Association between User and Role with tenant boundary enforcement."""

    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("hospitals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=sa.func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_roles",
    )
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="user_roles",
    )

    __table_args__ = (
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        sa.Index("idx_user_roles_tenant_user", "hospital_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class UserPermissionOverride(Base, TimestampMixin, TenantMixin):
    """User-specific permission grant or revocation without modifying shared role definitions."""

    __tablename__ = "user_permission_overrides"

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
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_granted: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        comment="True if explicitly granted, False if explicitly revoked/denied",
    )
    constraints_override: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        sa.JSON,
        nullable=True,
        comment="Custom constraints for this user, overriding role-level constraints",
    )
    reason: Mapped[Optional[str]] = mapped_column(
        sa.String(255),
        nullable=True,
        comment="Audit explanation for this individual override",
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="permission_overrides",
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="overrides",
    )

    __table_args__ = (
        sa.UniqueConstraint("user_id", "permission_id", name="uq_user_permission_override"),
        sa.Index("idx_override_tenant_user", "hospital_id", "user_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<UserPermissionOverride(user_id={self.user_id}, permission_id={self.permission_id}, "
            f"granted={self.is_granted})>"
        )
