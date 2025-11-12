"""Comments domain entities."""

from datetime import UTC, datetime

from src.core.domain.entities import TimestampedEntity
from src.core.domain.exceptions import ValidationException


class Comment(TimestampedEntity):
    """Comment entity representing a comment on an article."""

    def __init__(
        self,
        body: str,
        author_id: int,
        article_id: int,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize comment.

        Args:
            body: The comment text.
            author_id: The ID of the comment author (user).
            article_id: The ID of the article being commented on.
            id: The comment's unique identifier.
            created_at: When the comment was created.
            updated_at: When the comment was last updated.

        Raises:
            ValidationException: If body is empty or whitespace.
        """
        super().__init__(id, created_at, updated_at)

        if not body or not body.strip():
            raise ValidationException("Comment body cannot be empty", field="body")

        self._body = body.strip()
        self._author_id = author_id
        self._article_id = article_id

    @property
    def body(self) -> str:
        """Get comment body."""
        return self._body

    @property
    def author_id(self) -> int:
        """Get author ID."""
        return self._author_id

    @property
    def article_id(self) -> int:
        """Get article ID."""
        return self._article_id

    def update_body(self, new_body: str) -> None:
        """Update comment body.

        Args:
            new_body: The new comment text.

        Raises:
            ValidationException: If new_body is empty or whitespace.
        """
        if not new_body or not new_body.strip():
            raise ValidationException("Comment body cannot be empty", field="body")

        self._body = new_body.strip()
        self._updated_at = datetime.now(UTC)

    def __repr__(self) -> str:
        """String representation."""
        return f"Comment(id={self.id}, article_id={self.article_id}, author_id={self.author_id})"
