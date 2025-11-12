"""Get article query."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.articles.application.dtos import ArticleAuthorDTO, ArticleDTO
from src.modules.articles.domain.repositories import IArticleRepository
from src.modules.auth.domain.repositories import IUserRepository


class GetArticle(IUseCase[tuple[str, int | None], ArticleDTO]):
    """Use case for getting an article by slug."""

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

    async def execute(self, slug: str, current_user_id: int | None) -> ArticleDTO:
        """Execute the get article use case.

        Args:
            slug: The article's slug.
            current_user_id: The current user's ID (optional).

        Returns:
            The article DTO.

        Raises:
            EntityNotFoundException: If article is not found.
        """
        # Get article
        article = await self._article_repository.get_by_slug(slug)
        if not article:
            raise EntityNotFoundException("Article", slug)

        # Get author
        author = await self._user_repository.get(article.author_id)
        if not author:
            raise EntityNotFoundException("User", article.author_id)

        # Check if current user has favorited
        favorited = False
        if current_user_id:
            favorited = article.is_favorited_by(current_user_id)

        # Return DTO
        return ArticleDTO(
            id=article.id,  # type: ignore
            slug=article.slug.value,
            title=article.title,
            description=article.description,
            body=article.body,
            tags=list(article.tags),
            created_at=article.created_at,
            updated_at=article.updated_at,
            favorited=favorited,
            favorites_count=article.favorites_count(),
            author=ArticleAuthorDTO(
                name=author.name,
                bio=author.bio,
                image=author.image,
                following=False,  # Will be populated in route
            ),
        )
