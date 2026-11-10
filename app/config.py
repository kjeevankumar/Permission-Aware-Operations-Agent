"""Application configuration module using Pydantic Settings."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings and environment variables."""

    # Project Information
    PROJECT_NAME: str = "Permission-Aware Operations Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, test, production")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & JWT
    SECRET_KEY: str = Field(
        default="demo-super-secret-key-change-this-in-production-min-32-chars-long!",
        description="Cryptographic secret key for signing JWT tokens",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "hospital_ops"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/hospital_ops",
        description="Database connection URL",
    )
    TEST_DATABASE_URL: str = Field(
        default="sqlite:///./test_hospital_ops.db",
        description="Database connection URL for running tests",
    )

    # Database Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Pending Operations Expiration (minutes)
    PENDING_OPERATION_TTL_MINUTES: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
