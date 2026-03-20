"""Tests for profiles domain."""

import pytest

from src.modules.profiles.domain.entities import Profile
from src.modules.profiles.domain.exceptions import CannotFollowSelfException


class TestProfile:
    """Tests for Profile entity."""

    def test_create_profile(self) -> None:
        """Test creating a profile."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        assert profile.user_id == 1
        assert profile.email == "test@example.com"
        assert profile.name == "Test User"
        assert profile.bio is None
        assert profile.image is None
        assert profile.followers == set()
        assert profile.following == set()

    def test_profile_with_bio_and_image(self) -> None:
        """Test creating profile with bio and image."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
            bio="I love coding",
            image="https://example.com/avatar.jpg",
        )

        assert profile.bio == "I love coding"
        assert profile.image == "https://example.com/avatar.jpg"

    def test_follow_user(self) -> None:
        """Test following a user."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.follow(user_id=2)

        assert 2 in profile.following
        assert profile.is_following(2) is True
        assert profile.is_following(3) is False

    def test_unfollow_user(self) -> None:
        """Test unfollowing a user."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.follow(user_id=2)
        assert profile.is_following(2) is True

        profile.unfollow(user_id=2)
        assert profile.is_following(2) is False
        assert 2 not in profile.following

    def test_cannot_follow_self(self) -> None:
        """Test that a user cannot follow themselves."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        with pytest.raises(CannotFollowSelfException):
            profile.follow(user_id=1)

    def test_add_follower(self) -> None:
        """Test adding a follower."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.add_follower(user_id=2)

        assert 2 in profile.followers
        assert profile.has_follower(2) is True
        assert profile.has_follower(3) is False

    def test_remove_follower(self) -> None:
        """Test removing a follower."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.add_follower(user_id=2)
        assert profile.has_follower(2) is True

        profile.remove_follower(user_id=2)
        assert profile.has_follower(2) is False
        assert 2 not in profile.followers

    def test_idempotent_follow(self) -> None:
        """Test that following the same user multiple times is idempotent."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.follow(user_id=2)
        profile.follow(user_id=2)  # Follow again

        assert len(profile.following) == 1
        assert 2 in profile.following

    def test_idempotent_unfollow(self) -> None:
        """Test that unfollowing a user not followed is safe."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        # Unfollow without following first
        profile.unfollow(user_id=2)
        assert profile.is_following(2) is False

    def test_follower_count(self) -> None:
        """Test counting followers."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.add_follower(user_id=2)
        profile.add_follower(user_id=3)
        profile.add_follower(user_id=4)

        assert profile.follower_count() == 3

    def test_following_count(self) -> None:
        """Test counting following."""
        profile = Profile(
            user_id=1,
            email="test@example.com",
            name="Test User",
        )

        profile.follow(user_id=2)
        profile.follow(user_id=3)

        assert profile.following_count() == 2
