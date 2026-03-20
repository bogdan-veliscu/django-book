"""Create article command."""

from src.core.application.use_case import IUseCase
from src.modules.articles.application.dtos import (
    ArticleAuthorDTO,
    ArticleDTO,
    CreateArticleRequest,
)
from src.modules.articles.domain.entities import Article
from src.modules.articles.domain.repositories import IArticleRepository


class CreateArticle(IUseCase[CreateArticleRequest, ArticleDTO]):
    """Use case for creating a new article."""

    def __init__(self, article_repository: IArticleRepository) -> None:
        """Initialize use case.

        Args:
            article_repository: The article repository.
        """
        self._article_repository = article_repository

    async def execute(self, request: CreateArticleRequest) -> ArticleDTO:
        """Execute the create article use case.

        Args:
            request: The create article request.

        Returns:
            The created article DTO.
        """
        # Create article entity
        article = Article(
            title=request.title,
            description=request.description,
            body=request.body,
            author_id=request.author_id,
        )

        # Add tags
        for tag in request.tags:
            article.add_tag(tag)

        # Save article
        saved_article = await self._article_repository.add(article)

        # Return DTO (with placeholder author, will be populated in route)
        return ArticleDTO(
            id=saved_article.id,  # type: ignore
            slug=saved_article.slug.value,
            title=saved_article.title,
            description=saved_article.description,
            body=saved_article.body,
            tags=list(saved_article.tags),
            created_at=saved_article.created_at,
            updated_at=saved_article.updated_at,
            favorited=False,
            favorites_count=saved_article.favorites_count(),
            author=ArticleAuthorDTO(name=""),  # Placeholder, will be populated in route
        )
