"""Base value objects."""

from abc import ABC
from typing import Any


class ValueObject(ABC):
    """Base class for value objects.

    Value objects are immutable objects that are defined by their attributes
    rather than a unique identity. Two value objects with the same attributes
    are considered equal.
    """

    def __eq__(self, other: object) -> bool:
        """Value objects are equal if all their attributes are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash based on all attributes."""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self) -> str:
        """String representation."""
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
