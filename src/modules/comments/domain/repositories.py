"""Comment domain repository interfaces."""

from abc import abstractmethod

from src.core.infrastructure.repository import IRepository
from src.modules.comments.domain.entities import Comment


class ICommentRepository(IRepository[Comment]):
    """Repository interface for Comment entities."""

    @abstractmethod
    async def list_by_article(
        self, article_id: int, limit: int = 20, offset: int = 0
    ) -> list[Comment]:
        """List comments for an article.

        Args:
            article_id: The article's ID.
            limit: Maximum number of comments to return.
            offset: Number of comments to skip.

        Returns:
            List of comments ordered by creation date (newest first).
        """
        pass

    @abstractmethod
    async def list_by_author(
        self, author_id: int, limit: int = 20, offset: int = 0
    ) -> list[Comment]:
        """List comments by author.

        Args:
            author_id: The author's user ID.
            limit: Maximum number of comments to return.
            offset: Number of comments to skip.

        Returns:
            List of comments ordered by creation date (newest first).
        """
        pass

    @abstractmethod
    async def count_by_article(self, article_id: int) -> int:
        """Count comments for an article.

        Args:
            article_id: The article's ID.

        Returns:
            Number of comments on the article.
        """
        pass
