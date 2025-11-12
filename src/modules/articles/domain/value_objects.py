"""Articles domain value objects."""

import re
from slugify import slugify as python_slugify

from src.core.domain.value_objects import ValueObject


class Slug(ValueObject):
    """Slug value object for URL-friendly article identifiers."""

    def __init__(self, value: str) -> None:
        """Initialize slug.

        Args:
            value: The slug value.
        """
        self._value = value

    @classmethod
    def from_text(cls, text: str) -> "Slug":
        """Create a slug from text.

        Args:
            text: The text to slugify.

        Returns:
            A new Slug instance.
        """
        slug_value = python_slugify(text, separator="-")
        return cls(slug_value)

    @property
    def value(self) -> str:
        """Get the slug value."""
        return self._value

    def __str__(self) -> str:
        """String representation."""
        return self._value
