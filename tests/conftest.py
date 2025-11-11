"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.infrastructure.cache import CacheManager
from src.core.infrastructure.database import Base, DatabaseManager


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings."""
    return Settings(
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/conduit_test",
        redis_url="redis://localhost:6379/1",  # Use database 1 for tests
        debug=True,
        environment="development",
    )


@pytest_asyncio.fixture(scope="session")
async def db_manager(test_settings: Settings) -> AsyncGenerator[DatabaseManager, None]:
    """Create a test database manager."""
    manager = DatabaseManager(
        database_url=str(test_settings.database_url),
        echo=test_settings.database_echo,
    )

    # Create all tables
    await manager.create_all()

    yield manager

    # Drop all tables and close connections
    await manager.drop_all()
    await manager.close()


@pytest_asyncio.fixture
async def db_session(db_manager: DatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with db_manager.session() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes


@pytest_asyncio.fixture(scope="session")
async def cache_manager(test_settings: Settings) -> AsyncGenerator[CacheManager, None]:
    """Create a test cache manager."""
    manager = CacheManager(redis_url=str(test_settings.redis_url))
    yield manager
    # Clear all test cache keys
    await manager.delete_pattern("*")
    await manager.close()


@pytest_asyncio.fixture
async def client(
    test_settings: Settings,
    db_manager: DatabaseManager,
    cache_manager: CacheManager,
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    # Import here to avoid circular imports
    from src.main import create_app

    # Override settings
    def override_get_settings() -> Settings:
        return test_settings

    app = create_app()
    app.dependency_overrides[get_settings] = override_get_settings

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio as the async backend."""
    return "asyncio"
