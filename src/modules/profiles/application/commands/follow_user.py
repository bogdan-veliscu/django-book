"""Follow user command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.profiles.application.dtos import FollowUserRequest, ProfileDTO
from src.modules.profiles.domain.exceptions import CannotFollowSelfException
from src.modules.profiles.domain.repositories import IProfileRepository


class FollowUser(IUseCase[FollowUserRequest, ProfileDTO]):
    """Use case for following a user."""

    def __init__(self, profile_repository: IProfileRepository) -> None:
        """Initialize use case.

        Args:
            profile_repository: The profile repository.
        """
        self._profile_repository = profile_repository

    async def execute(self, request: FollowUserRequest) -> ProfileDTO:
        """Execute the follow user use case.

        Args:
            request: The follow user request.

        Returns:
            The followed profile DTO.

        Raises:
            EntityNotFoundException: If profile is not found.
            CannotFollowSelfException: If trying to follow self.
        """
        # Get profile to follow
        profile = await self._profile_repository.get_by_name(request.followee_name)
        if not profile:
            raise EntityNotFoundException("Profile", request.followee_name)

        # Check if trying to follow self
        if profile.user_id == request.follower_id:
            raise CannotFollowSelfException()

        # Create follow relationship
        await self._profile_repository.follow(request.follower_id, profile.user_id)

        # Check if now following (should be True)
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
