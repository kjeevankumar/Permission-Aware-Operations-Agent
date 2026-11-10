"""Application domain and security exception definitions."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(AppException):
    """Raised when authentication credentials cannot be validated."""
    pass


class TenantAccessViolationError(AppException):
    """Raised when a cross-tenant data access attempt is detected."""
    pass


class PermissionDeniedError(AppException):
    """Raised when an authenticated user lacks required permissions."""
    pass


class ConstraintViolationError(AppException):
    """Raised when an operation violates role or policy constraints."""
    pass


class EntityNotFoundError(AppException):
    """Raised when a requested resource does not exist within the tenant."""
    pass


class OperationExpiredError(AppException):
    """Raised when confirming an operation past its TTL."""
    pass


class DatabaseTransactionError(AppException):
    """Raised on atomic transaction failures."""
    pass


def http_exception_from_app_error(err: AppException) -> HTTPException:
    """Map domain exceptions to corresponding FastAPI HTTP exceptions."""
    if isinstance(err, AuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if isinstance(err, TenantAccessViolationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Tenant isolation boundary violation.",
        )
    if isinstance(err, PermissionDeniedError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.message,
        )
    if isinstance(err, ConstraintViolationError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Constraint violation", "message": err.message, "details": err.details},
        )
    if isinstance(err, EntityNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.message,
        )
    if isinstance(err, OperationExpiredError):
        return HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=err.message,
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=err.message,
    )
