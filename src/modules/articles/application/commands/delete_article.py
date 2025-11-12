"""Delete article command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.modules.articles.domain.repositories import IArticleRepository


class DeleteArticle(IUseCase[tuple[str, int], None]):
    """Use case for deleting an article."""

    def __init__(self, article_repository: IArticleRepository) -> None:
        """Initialize use case.

        Args:
            article_repository: The article repository.
        """
        self._article_repository = article_repository

    async def execute(self, slug: str, current_user_id: int) -> None:
        """Execute the delete article use case.

        Args:
            slug: The article's slug.
            current_user_id: The current user's ID.

        Raises:
            EntityNotFoundException: If article is not found.
            AuthorizationException: If user is not the author.
        """
        # Get article
        article = await self._article_repository.get_by_slug(slug)
        if not article:
            raise EntityNotFoundException("Article", slug)

        # Check authorization
        if article.author_id != current_user_id:
            raise AuthorizationException("Only the author can delete this article")

        # Delete article
        await self._article_repository.delete(article.id)  # type: ignore
