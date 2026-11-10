"""FastAPI application entrypoint for Permission-Aware Operations Agent."""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlalchemy as sa
from app.config import settings
from app.database.connection import engine
from app.api import api_router
from app.core.exceptions import AppException, http_exception_from_app_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify database connectivity on startup."""
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
    except Exception as exc:
        print(f"Database connection warning on startup: {exc}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Production-oriented foundation for AI-powered Hospital Database Operations Platform. "
        "Strictly enforces role-based access control (RBAC), multi-tenant isolation, operation previews, "
        "atomic transactions, and immutable audit logs."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Catch unhandled domain AppException and format as proper HTTP response."""
    http_exc = http_exception_from_app_error(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": http_exc.detail},
        headers=getattr(http_exc, "headers", None),
    )


# Health Check Endpoints
@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Basic health check and database connectivity verification."""
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


@app.get("/", tags=["Root"])
def root() -> Dict[str, Any]:
    """Root metadata endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


# Include V1 API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
