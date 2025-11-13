"""Authentication dependencies for FastAPI routes."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database import get_db_session
from src.core.presentation.dependencies import (
    get_current_user_id,
    get_current_user_id_optional,
)
from src.modules.auth.domain.repositories import IUserRepository
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


async def get_current_user(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
) -> dict:
    """Get current authenticated user as a dictionary.

    Args:
        current_user_id: The current user's ID from JWT token.
        user_repository: The user repository.

    Returns:
        Dictionary containing user information.

    Raises:
        HTTPException: If user not found.
    """
    user = await user_repository.get(current_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "id": user.id,
        "email": user.email.value,
        "name": user.name,
        "bio": user.bio,
        "image": user.image,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


async def get_optional_user(
    current_user_id: Annotated[int | None, Depends(get_current_user_id_optional)],
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
) -> dict | None:
    """Get current authenticated user as a dictionary (optional).

    Args:
        current_user_id: The current user's ID from JWT token (optional).
        user_repository: The user repository.

    Returns:
        Dictionary containing user information if authenticated, None otherwise.
    """
    if not current_user_id:
        return None

    user = await user_repository.get(current_user_id)

    if not user:
        return None

    return {
        "id": user.id,
        "email": user.email.value,
        "name": user.name,
        "bio": user.bio,
        "image": user.image,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
