"""Unfollow user command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.profiles.application.dtos import ProfileDTO, UnfollowUserRequest
from src.modules.profiles.domain.repositories import IProfileRepository


class UnfollowUser(IUseCase[UnfollowUserRequest, ProfileDTO]):
    """Use case for unfollowing a user."""

    def __init__(self, profile_repository: IProfileRepository) -> None:
        """Initialize use case.

        Args:
            profile_repository: The profile repository.
        """
        self._profile_repository = profile_repository

    async def execute(self, request: UnfollowUserRequest) -> ProfileDTO:
        """Execute the unfollow user use case.

        Args:
            request: The unfollow user request.

        Returns:
            The unfollowed profile DTO.

        Raises:
            EntityNotFoundException: If profile is not found.
        """
        # Get profile to unfollow
        profile = await self._profile_repository.get_by_name(request.followee_name)
        if not profile:
            raise EntityNotFoundException("Profile", request.followee_name)

        # Remove follow relationship
        await self._profile_repository.unfollow(request.follower_id, profile.user_id)

        # Check if now following (should be False)
        is_following = await self._profile_repository.is_following(
            request.follower_id, profile.user_id
        )

        return ProfileDTO(
            user_id=profile.user_id,
            email=profile.email,
            name=profile.name,
            bio=profile.bio,
            image=profile.image,
            following=is_following,
        )
