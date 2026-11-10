"""Database engine and session management."""

import json
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings


def custom_json_serializer(obj: Any) -> str:
    """Serialize objects including UUID, Decimal, and datetime to JSON."""
    def default_handler(o):
        if isinstance(o, (uuid.UUID, Decimal)):
            return str(o)
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    return json.dumps(obj, default=default_handler)


# Configure engine options based on dialect
engine_kwargs = {
    "json_serializer": custom_json_serializer,
}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_pre_ping": settings.DB_POOL_PRE_PING,
        }
    )

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a transactional database session."""
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
