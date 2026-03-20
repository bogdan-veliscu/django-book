"""Base repository interfaces."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.core.domain.entities import Entity

TEntity = TypeVar("TEntity", bound=Entity)


class IRepository(ABC, Generic[TEntity]):
    """Base repository interface.

    Repositories provide a collection-like interface for accessing domain entities.
    They abstract away the data access details and provide a clean API for the
    application layer.
    """

    @abstractmethod
    async def add(self, entity: TEntity) -> TEntity:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.

        Returns:
            The added entity with its ID populated.
        """
        pass

    @abstractmethod
    async def get(self, id: int) -> TEntity | None:
        """Get an entity by ID.

        Args:
            id: The ID of the entity to retrieve.

        Returns:
            The entity if found, None otherwise.
        """
        pass

    @abstractmethod
    async def update(self, entity: TEntity) -> TEntity:
        """Update an existing entity.

        Args:
            entity: The entity to update.

        Returns:
            The updated entity.
        """
        pass

    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete an entity by ID.

        Args:
            id: The ID of the entity to delete.
        """
        pass

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> list[TEntity]:
        """List entities with pagination.

        Args:
            limit: Maximum number of entities to return.
            offset: Number of entities to skip.

        Returns:
            List of entities.
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """Count total number of entities.

        Returns:
            Total count of entities.
        """
        pass
