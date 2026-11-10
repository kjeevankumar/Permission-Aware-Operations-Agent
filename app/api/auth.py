"""Authentication and user context API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import settings
from app.database.connection import get_db
from app.core.security import create_access_token
from app.core.dependencies import get_current_user_context
from app.security.authentication import authenticate_user, UserContext
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserContextResponse
from app.services.audit import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate user with username and password, returning signed JWT access token.
    Tenant isolation is guaranteed by binding hospital_id from the verified DB record.
    """
    user = authenticate_user(db, username=login_data.username, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or suspended",
        )

    access_token = create_access_token(
        subject=str(user.id),
        hospital_id=str(user.hospital_id),
    )

    log_audit_event(
        db=db,
        hospital_id=user.hospital_id,
        user_id=user.id,
        action="auth.login",
        resource_type="users",
        resource_id=str(user.id),
        status="SUCCESS",
    )
    db.commit()

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/token", response_model=Token, summary="OAuth2 password token endpoint for Swagger UI")
def login_oauth2_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """OAuth2 compatible token endpoint used by Swagger UI Authorize button."""
    return login_for_access_token(
        LoginRequest(username=form_data.username, password=form_data.password),
        db=db,
    )


@router.get("/me", response_model=UserContextResponse)
def read_current_user_context(
    context: UserContext = Depends(get_current_user_context),
) -> UserContextResponse:
    """
    Return verified security context for currently authenticated user.
    Includes active roles, effective permissions, and resolved constraints.
    """
    return UserContextResponse(
        user_id=context.user_id,
        hospital_id=context.hospital_id,
        username=context.username,
        email=context.email,
        full_name=context.full_name,
        active_roles=context.active_roles,
        permissions=context.permissions,
        account_status=context.account_status,
    )
