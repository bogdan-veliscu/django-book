"""Tests for auth use cases."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.config import Settings
from src.core.domain.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ValidationException,
)
from src.modules.auth.application.commands.register_user import RegisterUser
from src.modules.auth.application.commands.login_user import LoginUser
from src.modules.auth.application.dtos import LoginUserRequest, RegisterUserRequest
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email, Password
from src.modules.auth.infrastructure.jwt import JWTService


class TestRegisterUser:
    """Tests for RegisterUser use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def mock_jwt_service(self) -> MagicMock:
        """Create a mock JWT service."""
        service = MagicMock(spec=JWTService)
        service.create_access_token.return_value = "mock-token"
        return service

    @pytest.fixture
    def use_case(
        self,
        mock_repository: AsyncMock,
        mock_jwt_service: MagicMock,
    ) -> RegisterUser:
        """Create RegisterUser use case."""
        return RegisterUser(mock_repository, mock_jwt_service)

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        use_case: RegisterUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test successful user registration."""
        # Arrange
        request = RegisterUserRequest(
            email="test@example.com",
            name="Test User",
            password="password123",
        )

        mock_repository.exists_by_email.return_value = False
        mock_repository.add.return_value = User(
            id=1,
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.user.email == "test@example.com"
        assert result.user.name == "Test User"
        assert result.token == "mock-token"
        mock_repository.exists_by_email.assert_called_once()
        mock_repository.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(
        self,
        use_case: RegisterUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test registration with existing email."""
        # Arrange
        request = RegisterUserRequest(
            email="test@example.com",
            name="Test User",
            password="password123",
        )

        mock_repository.exists_by_email.return_value = True

        # Act & Assert
        with pytest.raises(EntityAlreadyExistsException):
            await use_case.execute(request)

        mock_repository.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self,
        use_case: RegisterUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test registration with invalid email."""
        # Arrange
        request = RegisterUserRequest(
            email="not-an-email",
            name="Test User",
            password="password123",
        )

        # Act & Assert
        with pytest.raises(ValidationException):
            await use_case.execute(request)

        mock_repository.exists_by_email.assert_not_called()
        mock_repository.add.assert_not_called()


class TestLoginUser:
    """Tests for LoginUser use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def mock_jwt_service(self) -> MagicMock:
        """Create a mock JWT service."""
        service = MagicMock(spec=JWTService)
        service.create_access_token.return_value = "mock-token"
        return service

    @pytest.fixture
    def use_case(
        self,
        mock_repository: AsyncMock,
        mock_jwt_service: MagicMock,
    ) -> LoginUser:
        """Create LoginUser use case."""
        return LoginUser(mock_repository, mock_jwt_service)

    @pytest.mark.asyncio
    async def test_login_user_success(
        self,
        use_case: LoginUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test successful user login."""
        # Arrange
        request = LoginUserRequest(
            email="test@example.com",
            password="password123",
        )

        user = User(
            id=1,
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )
        mock_repository.get_by_email.return_value = user

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.user.email == "test@example.com"
        assert result.user.name == "Test User"
        assert result.token == "mock-token"
        mock_repository.get_by_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self,
        use_case: LoginUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test login with non-existent email."""
        # Arrange
        request = LoginUserRequest(
            email="nonexistent@example.com",
            password="password123",
        )

        mock_repository.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(ValidationException, match="Invalid email or password"):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_login_user_invalid_password(
        self,
        use_case: LoginUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test login with incorrect password."""
        # Arrange
        request = LoginUserRequest(
            email="test@example.com",
            password="wrongpassword",
        )

        user = User(
            id=1,
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("correctpassword"),
        )
        mock_repository.get_by_email.return_value = user

        # Act & Assert
        with pytest.raises(ValidationException, match="Invalid email or password"):
            await use_case.execute(request)


class TestUpdateUser:
    """Tests for UpdateUser use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def existing_user(self) -> User:
        """Create an existing user entity."""
        return User(
            id=1,
            email=Email("existing@example.com"),
            name="existinguser",
            password=Password.from_raw("OldPassword123"),
            bio="Original bio",
            image="https://example.com/original.png",
        )

    @pytest.fixture
    def use_case(self, mock_repository: AsyncMock):
        """Create UpdateUser use case."""
        from src.modules.auth.application.commands.update_user import UpdateUser
        return UpdateUser(mock_repository)

    @pytest.mark.asyncio
    async def test_update_bio(self, use_case, mock_repository, existing_user) -> None:
        """Test updating user bio."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(bio="New bio text"))

        mock_repository.get.assert_called_once_with(1)
        mock_repository.update.assert_called_once()
        assert existing_user.bio == "New bio text"

    @pytest.mark.asyncio
    async def test_update_image(self, use_case, mock_repository, existing_user) -> None:
        """Test updating user image URL."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(image="https://example.com/new.png"))

        assert existing_user.image == "https://example.com/new.png"

    @pytest.mark.asyncio
    async def test_update_name(self, use_case, mock_repository, existing_user) -> None:
        """Test updating username."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(name="newusername"))

        assert existing_user.name == "newusername"

    @pytest.mark.asyncio
    async def test_update_email_success(self, use_case, mock_repository, existing_user) -> None:
        """Test updating email to an available address."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.get_by_email.return_value = None  # Email not taken
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(email="new@example.com"))

        assert existing_user.email.value == "new@example.com"
        mock_repository.get_by_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_email_already_taken(self, use_case, mock_repository, existing_user) -> None:
        """Test that updating to a taken email raises EntityAlreadyExistsException."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        other_user = User(
            id=2,
            email=Email("taken@example.com"),
            name="otheruser",
            password=Password.from_raw("Password123"),
        )
        mock_repository.get.return_value = existing_user
        mock_repository.get_by_email.return_value = other_user

        with pytest.raises(EntityAlreadyExistsException):
            await use_case.execute(1, UpdateUserRequest(email="taken@example.com"))

        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_email_same_user_allowed(self, use_case, mock_repository, existing_user) -> None:
        """Test that updating to the current user's own email is allowed."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.get_by_email.return_value = existing_user  # Same user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(email="existing@example.com"))

        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_password(self, use_case, mock_repository, existing_user) -> None:
        """Test updating password hashes the new value."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(password="NewPassword456"))

        assert existing_user.verify_password("NewPassword456")
        assert not existing_user.verify_password("OldPassword123")

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self, use_case, mock_repository, existing_user) -> None:
        """Test updating multiple fields simultaneously."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = existing_user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest(bio="Updated bio", image="https://img.com/x.png", name="newname"))

        assert existing_user.bio == "Updated bio"
        assert existing_user.image == "https://img.com/x.png"
        assert existing_user.name == "newname"
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_update_calls_repository(self, use_case, mock_repository, existing_user) -> None:
        """Test that an empty update still persists (for updated_at timestamp)."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        original_bio = existing_user.bio
        mock_repository.get.return_value = existing_user
        mock_repository.update.return_value = existing_user

        await use_case.execute(1, UpdateUserRequest())

        assert existing_user.bio == original_bio
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_not_found(self, use_case, mock_repository) -> None:
        """Test that updating a non-existent user raises EntityNotFoundException."""
        from src.modules.auth.application.dtos import UpdateUserRequest

        mock_repository.get.return_value = None

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(999, UpdateUserRequest(bio="Some bio"))

        mock_repository.update.assert_not_called()
