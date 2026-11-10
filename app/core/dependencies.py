"""FastAPI dependencies for database access, authentication, and permission verification."""

import uuid
from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database.connection import get_db
from app.core.security import decode_access_token
from app.core.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    http_exception_from_app_error,
)
from app.security.authentication import UserContext, resolve_user_context

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=True,
)


def get_current_user_context(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserContext:
    """
    Dependency that decodes bearer token and constructs verified UserContext from DB.
    Never trusts client-supplied tenant or role headers.
    """
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Token payload missing subject identifier.")

        user_id = uuid.UUID(user_id_str)
        context = resolve_user_context(db, user_id)
        return context

    except AuthenticationError as exc:
        raise http_exception_from_app_error(exc)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permission(permission_code: str) -> Callable[[UserContext], UserContext]:
    """
    Factory creating a dependency that enforces a specific permission code.
    Raises 403 Forbidden if the user lacks the permission.
    """

    def permission_checker(
        context: UserContext = Depends(get_current_user_context),
    ) -> UserContext:
        if not context.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Missing required permission '{permission_code}'.",
            )
        return context

    return permission_checker
