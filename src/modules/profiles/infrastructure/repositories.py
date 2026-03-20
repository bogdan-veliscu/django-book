"""Repository implementations for profiles module."""

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.infrastructure.models import UserModel
from src.modules.profiles.domain.entities import Profile
from src.modules.profiles.domain.repositories import IProfileRepository
from src.modules.profiles.infrastructure.models import follow_association


class ProfileRepository(IProfileRepository):
    """SQLAlchemy implementation of IProfileRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: The database session.
        """
        self._session = session

    async def add(self, entity: Profile) -> Profile:
        """Add is not supported for profiles (use UserRepository).

        Profiles are derived from users, so they cannot be created directly.
        """
        raise NotImplementedError("Use UserRepository to create users")

    async def get(self, id: int) -> Profile | None:
        """Get a profile by user ID.

        Args:
            id: The user ID.

        Returns:
            The profile if found, None otherwise.
        """
        return await self.get_by_user_id(id)

    async def get_by_user_id(self, user_id: int) -> Profile | None:
        """Get a profile by user ID.

        Args:
            user_id: The user's ID.

        Returns:
            The profile if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Get followers and following
        followers = await self.get_followers(user_id)
        following = await self.get_following(user_id)

        return self._to_entity(model, followers, following)

    async def get_by_name(self, name: str) -> Profile | None:
        """Get a profile by username.

        Args:
            name: The user's name.

        Returns:
            The profile if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        # Get followers and following
        followers = await self.get_followers(model.id)
        following = await self.get_following(model.id)

        return self._to_entity(model, followers, following)

    async def update(self, entity: Profile) -> Profile:
        """Update is not supported for profiles (use UserRepository).

        Profiles are derived from users, so they cannot be updated directly.
        """
        raise NotImplementedError("Use UserRepository to update users")

    async def delete(self, id: int) -> None:
        """Delete is not supported for profiles (use UserRepository).

        Profiles are derived from users, so they cannot be deleted directly.
        """
        raise NotImplementedError("Use UserRepository to delete users")

    async def list(self, limit: int = 100, offset: int = 0) -> list[Profile]:
        """List profiles with pagination.

        Args:
            limit: Maximum number of profiles to return.
            offset: Number of profiles to skip.

        Returns:
            List of profiles.
        """
        stmt = select(UserModel).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        profiles = []
        for model in models:
            followers = await self.get_followers(model.id)
            following = await self.get_following(model.id)
            profiles.append(self._to_entity(model, followers, following))

        return profiles

    async def count(self) -> int:
        """Count total number of profiles.

        Returns:
            Total count of profiles.
        """
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())

    async def follow(self, follower_id: int, followee_id: int) -> None:
        """Create a follow relationship.

        Args:
            follower_id: The ID of the user who is following.
            followee_id: The ID of the user being followed.
        """
        stmt = insert(follow_association).values(
            follower_id=follower_id, followee_id=followee_id
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def unfollow(self, follower_id: int, followee_id: int) -> None:
        """Remove a follow relationship.

        Args:
            follower_id: The ID of the user who is unfollowing.
            followee_id: The ID of the user being unfollowed.
        """
        stmt = delete(follow_association).where(
            follow_association.c.follower_id == follower_id,
            follow_association.c.followee_id == followee_id,
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def is_following(self, follower_id: int, followee_id: int) -> bool:
        """Check if one user follows another.

        Args:
            follower_id: The ID of the potential follower.
            followee_id: The ID of the potential followee.

        Returns:
            True if follower follows followee, False otherwise.
        """
        stmt = select(follow_association).where(
            follow_association.c.follower_id == follower_id,
            follow_association.c.followee_id == followee_id,
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def get_followers(self, user_id: int) -> list[int]:
        """Get all follower IDs for a user.

        Args:
            user_id: The user's ID.

        Returns:
            List of follower user IDs.
        """
        stmt = select(follow_association.c.follower_id).where(
            follow_association.c.followee_id == user_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_following(self, user_id: int) -> list[int]:
        """Get all user IDs that a user is following.

        Args:
            user_id: The user's ID.

        Returns:
            List of user IDs being followed.
        """
        stmt = select(follow_association.c.followee_id).where(
            follow_association.c.follower_id == user_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def _to_entity(
        model: UserModel, followers: list[int], following: list[int]
    ) -> Profile:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: The SQLAlchemy UserModel.
            followers: List of follower IDs.
            following: List of following IDs.

        Returns:
            The Profile entity.
        """
        return Profile(
            user_id=model.id,
            email=model.email,
            name=model.name,
            bio=model.bio,
            image=model.image,
            followers=set(followers),
            following=set(following),
        )
