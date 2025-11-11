"""Auth domain repository interfaces."""

from abc import abstractmethod

from src.core.infrastructure.repository import IRepository
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.value_objects import Email


class IUserRepository(IRepository[User]):
    """Repository interface for User entities."""

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Get a user by email.

        Args:
            email: The user's email.

        Returns:
            The user if found, None otherwise.
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user exists by email.

        Args:
            email: The user's email.

        Returns:
            True if user exists, False otherwise.
        """
        pass
