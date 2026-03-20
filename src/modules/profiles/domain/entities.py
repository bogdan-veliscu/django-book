"""Profile domain entities."""

from src.core.domain.entities import Entity
from src.modules.profiles.domain.exceptions import CannotFollowSelfException


class Profile(Entity):
    """Profile entity representing a user's public profile.

    A Profile is a public view of a User with social features like
    followers and following.
    """

    def __init__(
        self,
        user_id: int,
        email: str,
        name: str,
        bio: str | None = None,
        image: str | None = None,
        followers: set[int] | None = None,
        following: set[int] | None = None,
    ) -> None:
        """Initialize profile.

        Args:
            user_id: The user's ID.
            email: User's email address.
            name: User's display name.
            bio: User's biography (optional).
            image: User's profile image URL (optional).
            followers: Set of user IDs who follow this user.
            following: Set of user IDs this user follows.
        """
        super().__init__(id=user_id)
        self._user_id = user_id
        self._email = email
        self._name = name
        self._bio = bio
        self._image = image
        self._followers = followers or set()
        self._following = following or set()

    @property
    def user_id(self) -> int:
        """Get user ID."""
        return self._user_id

    @property
    def email(self) -> str:
        """Get email."""
        return self._email

    @property
    def name(self) -> str:
        """Get name."""
        return self._name

    @property
    def bio(self) -> str | None:
        """Get bio."""
        return self._bio

    @property
    def image(self) -> str | None:
        """Get image URL."""
        return self._image

    @property
    def followers(self) -> set[int]:
        """Get followers set."""
        return self._followers.copy()

    @property
    def following(self) -> set[int]:
        """Get following set."""
        return self._following.copy()

    def follow(self, user_id: int) -> None:
        """Follow another user.

        Args:
            user_id: The ID of the user to follow.

        Raises:
            CannotFollowSelfException: If trying to follow self.
        """
        if user_id == self._user_id:
            raise CannotFollowSelfException()

        self._following.add(user_id)

    def unfollow(self, user_id: int) -> None:
        """Unfollow a user.

        Args:
            user_id: The ID of the user to unfollow.
        """
        self._following.discard(user_id)

    def is_following(self, user_id: int) -> bool:
        """Check if this profile is following a user.

        Args:
            user_id: The ID of the user to check.

        Returns:
            True if following, False otherwise.
        """
        return user_id in self._following

    def add_follower(self, user_id: int) -> None:
        """Add a follower to this profile.

        Args:
            user_id: The ID of the user who is following.
        """
        self._followers.add(user_id)

    def remove_follower(self, user_id: int) -> None:
        """Remove a follower from this profile.

        Args:
            user_id: The ID of the user to remove.
        """
        self._followers.discard(user_id)

    def has_follower(self, user_id: int) -> bool:
        """Check if a user is a follower.

        Args:
            user_id: The ID of the user to check.

        Returns:
            True if user is a follower, False otherwise.
        """
        return user_id in self._followers

    def follower_count(self) -> int:
        """Get the number of followers.

        Returns:
            The count of followers.
        """
        return len(self._followers)

    def following_count(self) -> int:
        """Get the number of users this profile is following.

        Returns:
            The count of following.
        """
        return len(self._following)

    def __repr__(self) -> str:
        """String representation."""
        return f"Profile(user_id={self.user_id}, name={self.name})"
