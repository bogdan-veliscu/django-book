"""Tests for profiles use cases."""

from unittest.mock import AsyncMock

import pytest

from src.core.domain.exceptions import EntityNotFoundException
from src.modules.profiles.application.commands.follow_user import FollowUser
from src.modules.profiles.application.commands.unfollow_user import UnfollowUser
from src.modules.profiles.application.dtos import (
    FollowUserRequest,
    GetProfileRequest,
    UnfollowUserRequest,
)
from src.modules.profiles.application.queries.get_profile import GetProfile
from src.modules.profiles.domain.entities import Profile
from src.modules.profiles.domain.exceptions import CannotFollowSelfException
from src.modules.profiles.domain.repositories import IProfileRepository


class TestGetProfile:
    """Tests for GetProfile use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock profile repository."""
        return AsyncMock(spec=IProfileRepository)

    @pytest.fixture
    def use_case(self, mock_repository: AsyncMock) -> GetProfile:
        """Create GetProfile use case."""
        return GetProfile(mock_repository)

    @pytest.mark.asyncio
    async def test_get_profile_success(
        self,
        use_case: GetProfile,
        mock_repository: AsyncMock,
    ) -> None:
        """Test successfully getting a profile."""
        # Arrange
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
            bio="I love coding",
            image="https://example.com/avatar.jpg",
        )
        mock_repository.get_by_name.return_value = profile
        mock_repository.is_following.return_value = False

        request = GetProfileRequest(name="Test User", current_user_id=2)

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.user_id == 1
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.bio == "I love coding"
        assert result.image == "https://example.com/avatar.jpg"
        assert result.following is False
        mock_repository.get_by_name.assert_called_once_with("Test User")

    @pytest.mark.asyncio
    async def test_get_profile_with_following(
        self,
        use_case: GetProfile,
        mock_repository: AsyncMock,
    ) -> None:
        """Test getting a profile when current user is following."""
        # Arrange
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )
        mock_repository.get_by_name.return_value = profile
        mock_repository.is_following.return_value = True

        request = GetProfileRequest(name="Test User", current_user_id=2)

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.following is True
        mock_repository.is_following.assert_called_once_with(2, 1)

    @pytest.mark.asyncio
    async def test_get_profile_not_found(
        self,
        use_case: GetProfile,
        mock_repository: AsyncMock,
    ) -> None:
        """Test getting a non-existent profile."""
        # Arrange
        mock_repository.get_by_name.return_value = None
        request = GetProfileRequest(name="NonExistent")

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request)


class TestFollowUser:
    """Tests for FollowUser use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock profile repository."""
        return AsyncMock(spec=IProfileRepository)

    @pytest.fixture
    def use_case(self, mock_repository: AsyncMock) -> FollowUser:
        """Create FollowUser use case."""
        return FollowUser(mock_repository)

    @pytest.mark.asyncio
    async def test_follow_user_success(
        self,
        use_case: FollowUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test successfully following a user."""
        # Arrange
        profile = Profile(
            user_id=2,
            email="followee@example.com",
            name="Followee User",
        )
        mock_repository.get_by_name.return_value = profile
        mock_repository.is_following.return_value = True

        request = FollowUserRequest(follower_id=1, followee_name="Followee User")

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.user_id == 2
        assert result.name == "Followee User"
        assert result.following is True
        mock_repository.follow.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_follow_user_not_found(
        self,
        use_case: FollowUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test following a non-existent user."""
        # Arrange
        mock_repository.get_by_name.return_value = None
        request = FollowUserRequest(follower_id=1, followee_name="NonExistent")

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_cannot_follow_self(
        self,
        use_case: FollowUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test that a user cannot follow themselves."""
        # Arrange
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )
        mock_repository.get_by_name.return_value = profile

        request = FollowUserRequest(follower_id=1, followee_name="Test User")

        # Act & Assert
        with pytest.raises(CannotFollowSelfException):
            await use_case.execute(request)


class TestUnfollowUser:
    """Tests for UnfollowUser use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock profile repository."""
        return AsyncMock(spec=IProfileRepository)

    @pytest.fixture
    def use_case(self, mock_repository: AsyncMock) -> UnfollowUser:
        """Create UnfollowUser use case."""
        return UnfollowUser(mock_repository)

    @pytest.mark.asyncio
    async def test_unfollow_user_success(
        self,
        use_case: UnfollowUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test successfully unfollowing a user."""
        # Arrange
        profile = Profile(
            user_id=2,
            email="followee@example.com",
            name="Followee User",
        )
        mock_repository.get_by_name.return_value = profile
        mock_repository.is_following.return_value = False

        request = UnfollowUserRequest(follower_id=1, followee_name="Followee User")

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.user_id == 2
        assert result.name == "Followee User"
        assert result.following is False
        mock_repository.unfollow.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_unfollow_user_not_found(
        self,
        use_case: UnfollowUser,
        mock_repository: AsyncMock,
    ) -> None:
        """Test unfollowing a non-existent user."""
        # Arrange
        mock_repository.get_by_name.return_value = None
        request = UnfollowUserRequest(follower_id=1, followee_name="NonExistent")

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request)
