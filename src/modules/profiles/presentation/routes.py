"""Profiles API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infrastructure.database import get_db_session
from src.core.presentation.dependencies import (
    get_current_user_id,
    get_current_user_id_optional,
)
from src.modules.profiles.application.commands.follow_user import FollowUser
from src.modules.profiles.application.commands.unfollow_user import UnfollowUser
from src.modules.profiles.application.dtos import (
    FollowUserRequest,
    GetProfileRequest,
    UnfollowUserRequest,
)
from src.modules.profiles.application.queries.get_profile import GetProfile
from src.modules.profiles.infrastructure.repositories import ProfileRepository
from src.modules.profiles.presentation.schemas import (
    ProfileResponse,
    ProfileResponseWrapper,
)

router = APIRouter()


async def get_profile_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileRepository:
    """Get profile repository dependency.

    Args:
        session: The database session.

    Returns:
        The profile repository.
    """
    return ProfileRepository(session)


@router.get(
    "/profiles/{name}",
    response_model=ProfileResponseWrapper,
    summary="Get user profile by name",
)
async def get_profile(
    name: str,
    current_user_id: Annotated[
        int | None, Depends(get_current_user_id_optional)
    ] = None,
    profile_repository: Annotated[
        ProfileRepository, Depends(get_profile_repository)
    ] = None,
) -> ProfileResponseWrapper:
    """Get a user's profile by name.

    Args:
        name: The user's name.
        current_user_id: The current user's ID (optional).
        profile_repository: The profile repository.

    Returns:
        The user's profile.
    """
    use_case = GetProfile(profile_repository)

    request = GetProfileRequest(name=name, current_user_id=current_user_id)
    result = await use_case.execute(request)

    return ProfileResponseWrapper(
        profile=ProfileResponse(
            name=result.name,
            bio=result.bio,
            image=result.image,
            following=result.following,
        )
    )


@router.post(
    "/profiles/{name}/follow",
    response_model=ProfileResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Follow a user",
)
async def follow_user(
    name: str,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    profile_repository: Annotated[
        ProfileRepository, Depends(get_profile_repository)
    ] = None,
) -> ProfileResponseWrapper:
    """Follow a user.

    Args:
        name: The name of the user to follow.
        current_user_id: The current user's ID.
        profile_repository: The profile repository.

    Returns:
        The followed user's profile.
    """
    use_case = FollowUser(profile_repository)

    request = FollowUserRequest(follower_id=current_user_id, followee_name=name)
    result = await use_case.execute(request)

    return ProfileResponseWrapper(
        profile=ProfileResponse(
            name=result.name,
            bio=result.bio,
            image=result.image,
            following=result.following,
        )
    )


@router.delete(
    "/profiles/{name}/follow",
    response_model=ProfileResponseWrapper,
    status_code=status.HTTP_200_OK,
    summary="Unfollow a user",
)
async def unfollow_user(
    name: str,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    profile_repository: Annotated[
        ProfileRepository, Depends(get_profile_repository)
    ] = None,
) -> ProfileResponseWrapper:
    """Unfollow a user.

    Args:
        name: The name of the user to unfollow.
        current_user_id: The current user's ID.
        profile_repository: The profile repository.

    Returns:
        The unfollowed user's profile.
    """
    use_case = UnfollowUser(profile_repository)

    request = UnfollowUserRequest(follower_id=current_user_id, followee_name=name)
    result = await use_case.execute(request)

    return ProfileResponseWrapper(
        profile=ProfileResponse(
            name=result.name,
            bio=result.bio,
            image=result.image,
            following=result.following,
        )
    )
