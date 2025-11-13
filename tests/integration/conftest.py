"""Integration test fixtures and helpers."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.value_objects import Email, Password
from src.modules.auth.infrastructure.jwt import JWTService
from src.modules.auth.infrastructure.repositories import UserRepository


@pytest_asyncio.fixture
async def user_repository(db_session: AsyncSession) -> UserRepository:
    """Create a user repository for tests."""
    return UserRepository(db_session)


@pytest_asyncio.fixture
async def jwt_service(test_settings) -> JWTService:
    """Create a JWT service for tests."""
    return JWTService(test_settings)


@pytest_asyncio.fixture
async def test_user(
    user_repository: UserRepository,
    db_session: AsyncSession,
) -> User:
    """Create a test user."""
    user = User(
        email=Email("test@example.com"),
        name="testuser",
        password=Password("password123"),
    )
    created_user = await user_repository.add(user)
    await db_session.commit()
    return created_user


@pytest_asyncio.fixture
async def test_user2(
    user_repository: UserRepository,
    db_session: AsyncSession,
) -> User:
    """Create a second test user."""
    user = User(
        email=Email("test2@example.com"),
        name="testuser2",
        password=Password("password123"),
    )
    created_user = await user_repository.add(user)
    await db_session.commit()
    return created_user


@pytest_asyncio.fixture
async def test_user_token(test_user: User, jwt_service: JWTService) -> str:
    """Create an authentication token for the test user."""
    return jwt_service.create_access_token(test_user.id)  # type: ignore


@pytest_asyncio.fixture
async def test_user2_token(test_user2: User, jwt_service: JWTService) -> str:
    """Create an authentication token for the second test user."""
    return jwt_service.create_access_token(test_user2.id)  # type: ignore


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user_token: str,
) -> AsyncClient:
    """Create an authenticated HTTP client."""
    client.headers["Authorization"] = f"Token {test_user_token}"
    return client


@pytest_asyncio.fixture
async def authenticated_client2(
    client: AsyncClient,
    test_user2_token: str,
) -> AsyncClient:
    """Create an authenticated HTTP client for second user."""
    client.headers["Authorization"] = f"Token {test_user2_token}"
    return client


def get_auth_header(token: str) -> dict[str, str]:
    """Get authorization header with token.

    Args:
        token: The JWT token.

    Returns:
        Authorization header dict.
    """
    return {"Authorization": f"Token {token}"}
