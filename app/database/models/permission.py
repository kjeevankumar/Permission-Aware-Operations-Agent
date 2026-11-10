"""Permission and Role-Permission mapping models."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.role import Role
    from app.database.models.user import UserPermissionOverride


class Permission(Base):
    """Permission definition representing discrete actions within the system."""

    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(
        sa.String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        sa.String(50),
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
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    overrides: Mapped[List["UserPermissionOverride"]] = relationship(
        "UserPermissionOverride",
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Permission(code='{self.code}', category='{self.category}')>"


class RolePermission(Base):
    """Mapping between roles and permissions with role-specific constraints stored as JSON."""

    __tablename__ = "role_permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    constraints: Mapped[Dict[str, Any]] = mapped_column(
        sa.JSON,
        default=dict,
        nullable=False,
        server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=sa.func.now(),
    )

    # Relationships
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="role_permissions",
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions",
    )

    __table_args__ = (
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    def __repr__(self) -> str:
        return (
            f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id}, "
            f"constraints={self.constraints})>"
        )
