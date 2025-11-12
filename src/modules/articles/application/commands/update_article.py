"""Update article command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.modules.articles.application.dtos import (
    ArticleAuthorDTO,
    ArticleDTO,
    UpdateArticleRequest,
)
from src.modules.articles.domain.repositories import IArticleRepository


class UpdateArticle(IUseCase[tuple[str, int, UpdateArticleRequest], ArticleDTO]):
    """Use case for updating an article."""

    def __init__(self, article_repository: IArticleRepository) -> None:
        """Initialize use case.

        Args:
            article_repository: The article repository.
        """
        self._article_repository = article_repository

    async def execute(
        self, slug: str, current_user_id: int, request: UpdateArticleRequest
    ) -> ArticleDTO:
        """Execute the update article use case.

        Args:
            slug: The article's slug.
            current_user_id: The current user's ID.
            request: The update article request.

        Returns:
            The updated article DTO.

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
            raise AuthorizationException("Only the author can update this article")

        # Update article
        article.update(
            title=request.title,
            description=request.description,
            body=request.body,
        )

        # Save article
        updated_article = await self._article_repository.update(article)

        # Return DTO
        return ArticleDTO(
            id=updated_article.id,  # type: ignore
            slug=updated_article.slug.value,
            title=updated_article.title,
            description=updated_article.description,
            body=updated_article.body,
            tags=list(updated_article.tags),
            created_at=updated_article.created_at,
            updated_at=updated_article.updated_at,
            favorited=False,
            favorites_count=updated_article.favorites_count(),
            author=ArticleAuthorDTO(name=""),  # Placeholder, will be populated in route
        )
