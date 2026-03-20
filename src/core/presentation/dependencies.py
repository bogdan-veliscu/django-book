"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.domain.exceptions import ValidationException
from src.core.infrastructure.database import get_db_session
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.infrastructure.jwt import JWTService
from src.modules.auth.infrastructure.repositories import UserRepository


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IUserRepository:
    """Get user repository dependency.

    Args:
        session: The database session.

    Returns:
        The user repository.
    """
    return UserRepository(session)


def get_jwt_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JWTService:
    """Get JWT service dependency.

    Args:
        settings: Application settings.

    Returns:
        The JWT service.
    """
    return JWTService(settings)


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)] = None,
) -> int:
    """Get current user ID from authorization header.

    Args:
        authorization: The authorization header (format: "Token <jwt>").
        jwt_service: The JWT service.

    Returns:
        The current user's ID.

    Raises:
        HTTPException: If authorization header is missing or invalid.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # RealWorld API uses "Token <jwt>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Token <jwt>",
        )

    token = parts[1]

    try:
        user_id = jwt_service.get_user_id_from_token(token)
        return user_id
    except ValidationException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user_id_optional(
    authorization: Annotated[str | None, Header()] = None,
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)] = None,
) -> int | None:
    """Get current user ID from authorization header (optional).

    Args:
        authorization: The authorization header (format: "Token <jwt>").
        jwt_service: The JWT service.

    Returns:
        The current user's ID if authenticated, None otherwise.
    """
    if not authorization:
        return None

    try:
        return await get_current_user_id(authorization, jwt_service)
    except HTTPException:
        return None
