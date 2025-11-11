"""Login user command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import ValidationException
from src.modules.auth.application.dtos import AuthTokenDTO, LoginUserRequest, UserDTO
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email
from src.modules.auth.infrastructure.jwt import JWTService


class LoginUser(IUseCase[LoginUserRequest, AuthTokenDTO]):
    """Use case for logging in a user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        jwt_service: JWTService,
    ) -> None:
        """Initialize use case.

        Args:
            user_repository: The user repository.
            jwt_service: The JWT service.
        """
        self._user_repository = user_repository
        self._jwt_service = jwt_service

    async def execute(self, request: LoginUserRequest) -> AuthTokenDTO:
        """Execute the login user use case.

        Args:
            request: The login request.

        Returns:
            The authentication token and user data.

        Raises:
            ValidationException: If email or password is invalid.
        """
        # Create email value object (validates format)
        email = Email(request.email)

        # Get user by email
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise ValidationException("Invalid email or password")

        # Verify password
        if not user.verify_password(request.password):
            raise ValidationException("Invalid email or password")

        # Create JWT token
        token = self._jwt_service.create_access_token(
            user_id=user.id,  # type: ignore
            email=user.email.value,
        )

        # Return DTO
        return AuthTokenDTO(
            token=token,
            user=UserDTO(
                id=user.id,  # type: ignore
                email=user.email.value,
                name=user.name,
                bio=user.bio,
                image=user.image,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )
