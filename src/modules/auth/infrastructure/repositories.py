"""Repository implementations for auth module."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email, Password
from src.modules.auth.infrastructure.models import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: The database session.
        """
        self._session = session

    async def add(self, entity: User) -> User:
        """Add a new user to the repository.

        Args:
            entity: The user entity to add.

        Returns:
            The added user with its ID populated.
        """
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get(self, id: int) -> User | None:
        """Get a user by ID.

        Args:
            id: The ID of the user to retrieve.

        Returns:
            The user if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: Email) -> User | None:
        """Get a user by email.

        Args:
            email: The user's email.

        Returns:
            The user if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user exists by email.

        Args:
            email: The user's email.

        Returns:
            True if user exists, False otherwise.
        """
        user = await self.get_by_email(email)
        return user is not None

    async def update(self, entity: User) -> User:
        """Update an existing user.

        Args:
            entity: The user entity to update.

        Returns:
            The updated user.
        """
        stmt = select(UserModel).where(UserModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # Update model fields
        model.email = entity.email.value
        model.name = entity.name
        model.password_hash = entity.password.hashed
        model.bio = entity.bio
        model.image = entity.image
        model.updated_at = entity.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id: int) -> None:
        """Delete a user by ID.

        Args:
            id: The ID of the user to delete.
        """
        stmt = select(UserModel).where(UserModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()
        await self._session.delete(model)
        await self._session.flush()

    async def list(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List users with pagination.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            List of users.
        """
        stmt = select(UserModel).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count(self) -> int:
        """Count total number of users.

        Returns:
            Total count of users.
        """
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: The SQLAlchemy model.

        Returns:
            The domain entity.
        """
        return User(
            id=model.id,
            email=Email(model.email),
            name=model.name,
            password=Password.from_hash(model.password_hash),
            bio=model.bio,
            image=model.image,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model.

        Args:
            entity: The domain entity.

        Returns:
            The SQLAlchemy model.
        """
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            name=entity.name,
            password_hash=entity.password.hashed,
            bio=entity.bio,
            image=entity.image,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
