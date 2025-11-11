"""Profile domain repository interfaces."""

from abc import abstractmethod

from src.core.infrastructure.repository import IRepository
from src.modules.profiles.domain.entities import Profile


class IProfileRepository(IRepository[Profile]):
    """Repository interface for Profile entities."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Profile | None:
        """Get a profile by user ID.

        Args:
            user_id: The user's ID.

        Returns:
            The profile if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Profile | None:
        """Get a profile by username.

        Args:
            name: The user's name.

        Returns:
            The profile if found, None otherwise.
        """
        pass

    @abstractmethod
    async def follow(self, follower_id: int, followee_id: int) -> None:
        """Create a follow relationship.

        Args:
            follower_id: The ID of the user who is following.
            followee_id: The ID of the user being followed.
        """
        pass

    @abstractmethod
    async def unfollow(self, follower_id: int, followee_id: int) -> None:
        """Remove a follow relationship.

        Args:
            follower_id: The ID of the user who is unfollowing.
            followee_id: The ID of the user being unfollowed.
        """
        pass

    @abstractmethod
    async def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if one user follows another.

        Args:
            follower_id: The ID of the potential follower.
            followee_id: The ID of the potential followee.

        Returns:
            True if follower follows followee, False otherwise.
        """
        pass

    @abstractmethod
    async def get_followers(self, user_id: int) -> list[int]:
        """Get all follower IDs for a user.

        Args:
            user_id: The user's ID.

        Returns:
            List of follower user IDs.
        """
        pass

    @abstractmethod
    async def get_following(self, user_id: int) -> list[int]:
        """Get all user IDs that a user is following.

        Args:
            user_id: The user's ID.

        Returns:
            List of user IDs being followed.
        """
        pass
