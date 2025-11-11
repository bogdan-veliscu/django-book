"""Get profile query."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.profiles.application.dtos import GetProfileRequest, ProfileDTO
from src.modules.profiles.domain.repositories import IProfileRepository


class GetProfile(IUseCase[GetProfileRequest, ProfileDTO]):
    """Use case for getting a user's profile."""

    def __init__(self, profile_repository: IProfileRepository) -> None:
        """Initialize use case.

        Args:
            profile_repository: The profile repository.
        """
        self._profile_repository = profile_repository

    async def execute(self, request: GetProfileRequest) -> ProfileDTO:
        """Execute the get profile use case.

        Args:
            request: The get profile request.

        Returns:
            The profile DTO.

        Raises:
            EntityNotFoundException: If profile is not found.
        """
        # Get profile by name
        profile = await self._profile_repository.get_by_name(request.name)
        if not profile:
            raise EntityNotFoundException("Profile", request.name)

        # Check if current user is following this profile
        is_following = False
        if request.current_user_id:
            is_following = await self._profile_repository.is_following(
                request.current_user_id, profile.user_id
            )

        return ProfileDTO(
            user_id=profile.user_id,
            email=profile.email,
            name=profile.name,
            bio=profile.bio,
            image=profile.image,
            following=is_following,
        )
