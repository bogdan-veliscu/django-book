"""Unfavorite article command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.articles.application.dtos import ArticleAuthorDTO, ArticleDTO
from src.modules.articles.domain.repositories import IArticleRepository
from src.modules.auth.domain.repositories import IUserRepository


class UnfavoriteArticle(IUseCase[tuple[str, int], ArticleDTO]):
    """Use case for unfavoriting an article."""

    def __init__(
        self,
        article_repository: IArticleRepository,
        user_repository: IUserRepository,
    ) -> None:
        """Initialize use case.

        Args:
            article_repository: The article repository.
            user_repository: The user repository.
        """
        self._article_repository = article_repository
        self._user_repository = user_repository

    async def execute(self, slug: str, current_user_id: int) -> ArticleDTO:
        """Execute the unfavorite article use case.

        Args:
            slug: The article's slug.
            current_user_id: The current user's ID.

        Returns:
            The unfavorited article DTO.

        Raises:
            EntityNotFoundException: If article is not found.
        """
        # Get article
        article = await self._article_repository.get_by_slug(slug)
        if not article:
            raise EntityNotFoundException("Article", slug)

        # Unfavorite the article
        article.unfavorite(current_user_id)

        # Save article
        updated_article = await self._article_repository.update(article)

        # Get author
        author = await self._user_repository.get(updated_article.author_id)
        if not author:
            raise EntityNotFoundException("User", updated_article.author_id)

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
            author=ArticleAuthorDTO(
                name=author.name,
                bio=author.bio,
                image=author.image,
                following=False,  # Will be populated in route
            ),
        )
