"""Article domain repository interfaces."""

from abc import abstractmethod

from src.core.infrastructure.repository import IRepository
from src.modules.articles.domain.entities import Article, Tag


class IArticleRepository(IRepository[Article]):
    """Repository interface for Article entities."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Article | None:
        """Get an article by slug.

        Args:
            slug: The article's slug.

        Returns:
            The article if found, None otherwise.
        """
        pass

    @abstractmethod
    async def list_by_author(
        self, author_id: int, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List articles by author.

        Args:
            author_id: The author's user ID.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        pass

    @abstractmethod
    async def list_by_tag(
        self, tag: str, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List articles by tag.

        Args:
            tag: The tag name.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        pass

    @abstractmethod
    async def list_favorited_by(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List articles favorited by a user.

        Args:
            user_id: The user's ID.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        pass

    @abstractmethod
    async def get_feed(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """Get article feed for a user (from followed authors).

        Args:
            user_id: The user's ID.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles from followed authors.
        """
        pass

    @abstractmethod
    async def get_all_tags(self) -> list[str]:
        """Get all unique tags used in articles.

        Returns:
            List of tag names.
        """
        pass


class ITagRepository(IRepository[Tag]):
    """Repository interface for Tag entities."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Tag | None:
        """Get a tag by name.

        Args:
            name: The tag name.

        Returns:
            The tag if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_or_create(self, name: str) -> Tag:
        """Get a tag by name or create it if it doesn't exist.

        Args:
            name: The tag name.

        Returns:
            The tag (existing or newly created).
        """
        pass
