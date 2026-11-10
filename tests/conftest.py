"""Pytest fixtures and configuration for Permission-Aware Operations Agent."""

import os
import pytest
from typing import Generator
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.config import settings
from app.database.base import Base
from app.database.connection import get_db, custom_json_serializer
from app.database.seed import seed_database, DEMO_PASSWORD
from app.main import app
from app.core.security import create_access_token
from app.database.models import User, Hospital

# Test database setup (uses TEST_DATABASE_URL or an isolated SQLite file)
TEST_DB_FILE = "./test_hospital_ops.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = sa.create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    json_serializer=custom_json_serializer,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables and run seed data once for the test session."""
    # Ensure fresh test database file
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        seed_database(session)
    finally:
        session.close()

    yield

    # Clean up after test session
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Yield a database session for testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def metro_admin_token(db_session: Session) -> str:
    """Generate access token for Metro Health Admin user."""
    user = db_session.execute(
        sa.select(User).where(User.username == "admin.metro")
    ).scalar_one()
    return create_access_token(str(user.id), str(user.hospital_id))


@pytest.fixture
def metro_billing_token(db_session: Session) -> str:
    """Generate access token for Metro Health Billing Manager."""
    user = db_session.execute(
        sa.select(User).where(User.username == "billing.metro")
    ).scalar_one()
    return create_access_token(str(user.id), str(user.hospital_id))


@pytest.fixture
def metro_pharma_token(db_session: Session) -> str:
    """Generate access token for Metro Health Pharmacist."""
    user = db_session.execute(
        sa.select(User).where(User.username == "pharma.metro")
    ).scalar_one()
    return create_access_token(str(user.id), str(user.hospital_id))


@pytest.fixture
def metro_frontdesk_token(db_session: Session) -> str:
    """Generate access token for Metro Health Front Desk."""
    user = db_session.execute(
        sa.select(User).where(User.username == "frontdesk.metro")
    ).scalar_one()
    return create_access_token(str(user.id), str(user.hospital_id))


@pytest.fixture
def jude_admin_token(db_session: Session) -> str:
    """Generate access token for St. Jude Admin user."""
    user = db_session.execute(
        sa.select(User).where(User.username == "admin.jude")
    ).scalar_one()
    return create_access_token(str(user.id), str(user.hospital_id))
