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
