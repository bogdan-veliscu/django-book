"""Base domain entities."""

from abc import ABC
from datetime import UTC, datetime
from typing import Any


class Entity(ABC):
    """Base class for all domain entities.

    An entity is an object that has a distinct identity that runs through time
    and different representations. Entities are mutable.
    """

    def __init__(self, id: int | None = None) -> None:
        """Initialize entity with optional ID.

        Args:
            id: The unique identifier for this entity.
        """
        self._id = id

    @property
    def id(self) -> int | None:
        """Get entity ID."""
        return self._id

    def __eq__(self, other: object) -> bool:
        """Entities are equal if they have the same ID."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id and self.id is not None

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id) if self.id is not None else hash(id(self))


class AggregateRoot(Entity):
    """Base class for aggregate roots.

    An aggregate root is the main entity in an aggregate. All access to the
    aggregate should go through the root. This ensures consistency boundaries.
    """

    def __init__(self, id: int | None = None) -> None:
        """Initialize aggregate root."""
        super().__init__(id)
        self._domain_events: list[Any] = []

    @property
    def domain_events(self) -> list[Any]:
        """Get domain events raised by this aggregate."""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear domain events."""
        self._domain_events.clear()

    def _raise_event(self, event: Any) -> None:
        """Raise a domain event."""
        self._domain_events.append(event)


class TimestampedEntity(Entity):
    """Base class for entities with timestamps."""

    def __init__(
        self,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize timestamped entity.

        Args:
            id: The unique identifier for this entity.
            created_at: When the entity was created.
            updated_at: When the entity was last updated.
        """
        super().__init__(id)
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def mark_updated(self) -> None:
        """Mark entity as updated."""
        self._updated_at = datetime.now(UTC)
