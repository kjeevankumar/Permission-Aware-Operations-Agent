"""Multi-tenant isolation enforcement utilities."""

import uuid
from typing import Any
from sqlalchemy.sql import Select
from app.core.exceptions import TenantAccessViolationError


def scope_query_to_tenant(
    query: Select,
    model: Any,
    hospital_id: uuid.UUID,
) -> Select:
    """
    Apply strict tenant isolation filter to a SQLAlchemy Select statement.
    Guarantees queries cannot access data outside the authenticated hospital.
    """
    if not hasattr(model, "hospital_id"):
        raise ValueError(f"Model {model.__name__} does not contain a hospital_id tenant column.")
    return query.where(model.hospital_id == hospital_id)


def verify_tenant_boundary(
    entity: Any,
    expected_hospital_id: uuid.UUID,
) -> None:
    """
    Verify that an entity belongs to the expected hospital tenant.
    Raises TenantAccessViolationError on any cross-tenant access attempt.
    """
    if not hasattr(entity, "hospital_id"):
        raise ValueError("Entity does not have a hospital_id attribute.")

    if entity.hospital_id != expected_hospital_id:
        raise TenantAccessViolationError(
            f"Tenant boundary violation: entity belongs to {entity.hospital_id}, "
            f"expected {expected_hospital_id}"
        )
