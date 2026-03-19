"""Update user command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityAlreadyExistsException, EntityNotFoundException
from src.modules.auth.application.dtos import UpdateUserRequest, UserDTO
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email, Password


class UpdateUser(IUseCase[tuple[int, UpdateUserRequest], UserDTO]):
    """Use case for updating an existing user."""

    def __init__(self, user_repository: IUserRepository) -> None:
        """Initialize use case.

        Args:
            user_repository: The user repository.
        """
        self._user_repository = user_repository

    async def execute(self, user_id: int, request: UpdateUserRequest) -> UserDTO:
        """Execute the update user use case.

        Args:
            user_id: The ID of the user to update.
            request: The update request with optional fields.

        Returns:
            The updated user DTO.

        Raises:
            EntityNotFoundException: If user not found.
            EntityAlreadyExistsException: If new email is already taken.
        """
        user = await self._user_repository.get(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)

        if request.email is not None:
            new_email = Email(request.email)
            existing = await self._user_repository.get_by_email(new_email)
            if existing and existing.id != user_id:
                raise EntityAlreadyExistsException("User", request.email)
            user.update_email(new_email)

        if request.name is not None or request.bio is not None or request.image is not None:
            user.update_profile(
                name=request.name,
                bio=request.bio,
                image=request.image,
            )

        if request.password is not None:
            user.update_password(Password.from_raw(request.password))

        updated_user = await self._user_repository.update(user)

        return UserDTO(
            id=updated_user.id,  # type: ignore
            email=updated_user.email.value,
            name=updated_user.name,
            bio=updated_user.bio,
            image=updated_user.image,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )
