"""Application configuration."""

from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Conduit API"
    app_version: str = "0.2.0"
    debug: bool = False
    environment: str = Field(default="development", pattern="^(development|staging|production)$")

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/conduit"
    )
    database_echo: bool = False

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    # Authentication
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production-at-least-32-characters-long"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])

    # AWS S3 (for file uploads)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_bucket_name: str | None = None
    aws_s3_region: str = "us-east-1"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Cache TTL (in seconds)
    cache_ttl_articles: int = 60 * 5  # 5 minutes
    cache_ttl_profiles: int = 60 * 10  # 10 minutes
    cache_ttl_tags: int = 60 * 30  # 30 minutes


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        The application settings.
    """
    return Settings()
