"""Data Transfer Objects for articles module."""

from datetime import datetime

from src.core.application.dto import DTO


class ArticleAuthorDTO(DTO):
    """Article author data transfer object."""

    name: str
    bio: str | None = None
    image: str | None = None
    following: bool = False


class ArticleDTO(DTO):
    """Article data transfer object."""

    id: int
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    favorited: bool = False
    favorites_count: int = 0
    author: ArticleAuthorDTO


class CreateArticleRequest(DTO):
    """Request to create a new article."""

    title: str
    description: str
    body: str
    tags: list[str] = []
    author_id: int  # Set by authentication


class UpdateArticleRequest(DTO):
    """Request to update an article."""

    title: str | None = None
    description: str | None = None
    body: str | None = None


class ListArticlesRequest(DTO):
    """Request to list articles with filters."""

    tag: str | None = None
    author: str | None = None  # Author name
    favorited: str | None = None  # User name who favorited
    limit: int = 20
    offset: int = 0
    current_user_id: int | None = None  # For checking favorites and following


class GetArticleFeedRequest(DTO):
    """Request to get article feed."""

    user_id: int
    limit: int = 20
    offset: int = 0
