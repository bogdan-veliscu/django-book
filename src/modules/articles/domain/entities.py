"""Articles domain entities."""

from datetime import datetime

from src.core.domain.entities import AggregateRoot, TimestampedEntity
from src.modules.articles.domain.value_objects import Slug


class Tag(TimestampedEntity):
    """Tag entity for categorizing articles."""

    def __init__(
        self,
        name: str,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize tag.

        Args:
            name: The tag name (will be normalized to lowercase).
            id: The tag's unique identifier.
            created_at: When the tag was created.
            updated_at: When the tag was last updated.
        """
        super().__init__(id, created_at, updated_at)
        self._name = name.lower()

    @property
    def name(self) -> str:
        """Get tag name."""
        return self._name

    def __eq__(self, other: object) -> bool:
        """Tags are equal if they have the same name."""
        if not isinstance(other, Tag):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash based on name."""
        return hash(self.name)

    def __repr__(self) -> str:
        """String representation."""
        return f"Tag(name={self.name})"


class Article(AggregateRoot):
    """Article entity representing a blog post.

    An article is an aggregate root that manages its tags and favorites.
    """

    def __init__(
        self,
        title: str,
        description: str,
        body: str,
        author_id: int,
        id: int | None = None,
        slug: Slug | None = None,
        tags: set[str] | None = None,
        favorites: set[int] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize article.

        Args:
            title: The article title.
            description: Brief description/summary.
            body: The article content.
            author_id: The ID of the author (user).
            id: The article's unique identifier.
            slug: URL-friendly slug (auto-generated if not provided).
            tags: Set of tag names.
            favorites: Set of user IDs who favorited this article.
            created_at: When the article was created.
            updated_at: When the article was last updated.
        """
        super().__init__(id)
        self._title = title
        self._description = description
        self._body = body
        self._author_id = author_id
        self._slug = slug or Slug.from_text(title)
        self._tags = tags or set()
        self._favorites = favorites or set()
        self._created_at = created_at or datetime.now()
        self._updated_at = updated_at or datetime.now()

    @property
    def title(self) -> str:
        """Get article title."""
        return self._title

    @property
    def description(self) -> str:
        """Get article description."""
        return self._description

    @property
    def body(self) -> str:
        """Get article body."""
        return self._body

    @property
    def author_id(self) -> int:
        """Get author ID."""
        return self._author_id

    @property
    def slug(self) -> Slug:
        """Get article slug."""
        return self._slug

    @property
    def tags(self) -> set[str]:
        """Get article tags."""
        return self._tags.copy()

    @property
    def favorites(self) -> set[int]:
        """Get favorites set."""
        return self._favorites.copy()

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def add_tag(self, tag_name: str) -> None:
        """Add a tag to the article.

        Args:
            tag_name: The tag name to add (will be normalized to lowercase).
        """
        self._tags.add(tag_name.lower())

    def remove_tag(self, tag_name: str) -> None:
        """Remove a tag from the article.

        Args:
            tag_name: The tag name to remove.
        """
        self._tags.discard(tag_name.lower())

    def has_tag(self, tag_name: str) -> bool:
        """Check if article has a tag.

        Args:
            tag_name: The tag name to check.

        Returns:
            True if article has the tag, False otherwise.
        """
        return tag_name.lower() in self._tags

    def favorite(self, user_id: int) -> None:
        """Favorite this article by a user.

        Args:
            user_id: The ID of the user favoriting.
        """
        self._favorites.add(user_id)

    def unfavorite(self, user_id: int) -> None:
        """Unfavorite this article by a user.

        Args:
            user_id: The ID of the user unfavoriting.
        """
        self._favorites.discard(user_id)

    def is_favorited_by(self, user_id: int) -> bool:
        """Check if article is favorited by a user.

        Args:
            user_id: The user ID to check.

        Returns:
            True if favorited, False otherwise.
        """
        return user_id in self._favorites

    def favorites_count(self) -> int:
        """Get the number of favorites.

        Returns:
            The count of favorites.
        """
        return len(self._favorites)

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        body: str | None = None,
    ) -> None:
        """Update article content.

        Args:
            title: New title (optional).
            description: New description (optional).
            body: New body content (optional).
        """
        if title is not None:
            self._title = title
            self._slug = Slug.from_text(title)  # Regenerate slug

        if description is not None:
            self._description = description

        if body is not None:
            self._body = body

        self._updated_at = datetime.now()

    def __repr__(self) -> str:
        """String representation."""
        return f"Article(id={self.id}, title={self.title}, slug={self.slug.value})"
