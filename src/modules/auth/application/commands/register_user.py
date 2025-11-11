"""Register user command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityAlreadyExistsException
from src.modules.auth.application.dtos import AuthTokenDTO, RegisterUserRequest, UserDTO
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email, Password
from src.modules.auth.infrastructure.jwt import JWTService


class RegisterUser(IUseCase[RegisterUserRequest, AuthTokenDTO]):
    """Use case for registering a new user."""

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

    async def execute(self, request: RegisterUserRequest) -> AuthTokenDTO:
        """Execute the register user use case.

        Args:
            request: The registration request.

        Returns:
            The authentication token and user data.

        Raises:
            EntityAlreadyExistsException: If email already exists.
            ValidationException: If email or password is invalid.
        """
        # Create value objects (this validates the email and password)
        email = Email(request.email)
        password = Password.from_raw(request.password)

        # Check if user already exists
        if await self._user_repository.exists_by_email(email):
            raise EntityAlreadyExistsException("User", email.value)

        # Create user entity
        user = User(
            email=email,
            name=request.name,
            password=password,
        )

        # Save user
        saved_user = await self._user_repository.add(user)

        # Create JWT token
        token = self._jwt_service.create_access_token(
            user_id=saved_user.id,  # type: ignore
            email=saved_user.email.value,
        )

        # Return DTO
        return AuthTokenDTO(
            token=token,
            user=UserDTO(
                id=saved_user.id,  # type: ignore
                email=saved_user.email.value,
                name=saved_user.name,
                bio=saved_user.bio,
                image=saved_user.image,
                created_at=saved_user.created_at,
                updated_at=saved_user.updated_at,
            ),
        )
