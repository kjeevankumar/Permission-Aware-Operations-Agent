"""Tests verifying JWT authentication foundations, token validation, and user security context."""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
import sqlalchemy as sa
from app.database.models import User
from app.database.seed import DEMO_PASSWORD
from app.core.security import create_access_token, decode_access_token
from app.core.dependencies import get_current_user_context
from app.api.auth import login_for_access_token, read_current_user_context
from app.schemas.auth import LoginRequest


def test_login_success(db_session: Session):
    """Verify that a valid user can successfully authenticate and receive a JWT token."""
    login_req = LoginRequest(username="admin.metro", password=DEMO_PASSWORD)
    token = login_for_access_token(login_req, db=db_session)

    assert token.access_token is not None
    assert token.token_type == "bearer"
    assert token.expires_in > 0

    # Verify decoded token claims
    payload = decode_access_token(token.access_token)
    assert payload.get("sub") is not None
    assert payload.get("hospital_id") is not None

    # Clean up test audit log entry so audit table remains pristine for initial seed verification
    from app.database.models import AuditLog
    db_session.execute(sa.delete(AuditLog))
    db_session.commit()


def test_login_invalid_password(db_session: Session):
    """Verify that an incorrect password fails with 401 Unauthorized."""
    login_req = LoginRequest(username="admin.metro", password="WrongPassword123!")
    with pytest.raises(HTTPException) as exc_info:
        login_for_access_token(login_req, db=db_session)

    assert exc_info.value.status_code == 401
    assert "Incorrect username or password" in exc_info.value.detail


def test_login_nonexistent_user(db_session: Session):
    """Verify that an unknown username fails with 401 Unauthorized."""
    login_req = LoginRequest(username="ghost.user", password=DEMO_PASSWORD)
    with pytest.raises(HTTPException) as exc_info:
        login_for_access_token(login_req, db=db_session)

    assert exc_info.value.status_code == 401


def test_login_inactive_user(db_session: Session):
    """Verify that an inactive/suspended user cannot authenticate."""
    user = db_session.execute(
        sa.select(User).where(User.username == "pharma.metro")
    ).scalar_one()

    # Temporarily deactivate user
    user.is_active = False
    db_session.commit()

    try:
        login_req = LoginRequest(username="pharma.metro", password=DEMO_PASSWORD)
        with pytest.raises(HTTPException) as exc_info:
            login_for_access_token(login_req, db=db_session)

        assert exc_info.value.status_code == 403
        assert "inactive" in exc_info.value.detail.lower()
    finally:
        user.is_active = True
        db_session.commit()


def test_auth_me_returns_verified_context(db_session: Session, metro_admin_token: str):
    """
    Verify that /auth/me returns the verified context including user_id, hospital_id,
    active roles, and effective permissions derived strictly from the database.
    """
    context = get_current_user_context(token=metro_admin_token, db=db_session)
    response = read_current_user_context(context=context)

    assert response.username == "admin.metro"
    assert "Admin" in response.active_roles
    assert "inventory.read" in response.permissions
    assert "bills.read" in response.permissions
    assert "bills.discount" in response.permissions
    assert response.account_status == "active"
    assert response.hospital_id == context.hospital_id


def test_invalid_token_is_rejected(db_session: Session):
    """Verify that tampered or invalid JWT is rejected with 401 Unauthorized."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_context(token="invalid.tampered.token", db=db_session)

    assert exc_info.value.status_code == 401


def test_client_cannot_spoof_hospital_id(db_session: Session, metro_admin_token: str):
    """
    Verify that even if an attacker crafts an access token with an illegitimate hospital_id claim,
    the user context resolution ALWAYS fetches the immutable hospital_id from the verified database record.
    """
    admin_user = db_session.execute(
        sa.select(User).where(User.username == "admin.metro")
    ).scalar_one()

    fake_hospital_id = "00000000-0000-0000-0000-000000000000"
    # Maliciously attempt to forge hospital_id in the token payload
    forged_token = create_access_token(
        subject=str(admin_user.id),
        hospital_id=fake_hospital_id,
    )

    resolved_context = get_current_user_context(token=forged_token, db=db_session)
    # Must match the DB hospital_id, NOT the forged claim!
    assert resolved_context.hospital_id == admin_user.hospital_id
    assert str(resolved_context.hospital_id) != fake_hospital_id
