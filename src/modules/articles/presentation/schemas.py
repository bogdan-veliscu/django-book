"""Pydantic schemas for articles API."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileSchema(BaseModel):
    """Profile schema for article author."""

    username: str
    bio: str | None = None
    image: str | None = None
    following: bool


class ArticleSchema(BaseModel):
    """Article schema for API responses."""

    slug: str
    title: str
    description: str
    body: str
    tagList: list[str] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime
    favorited: bool
    favoritesCount: int
    author: ProfileSchema


class ArticleResponseSchema(BaseModel):
    """Single article response schema."""

    article: ArticleSchema


class MultipleArticlesResponseSchema(BaseModel):
    """Multiple articles response schema."""

    articles: list[ArticleSchema]
    articlesCount: int


class CreateArticleRequestSchema(BaseModel):
    """Request schema for creating an article."""

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    body: str = Field(min_length=1)
    tagList: list[str] = Field(default_factory=list)


class CreateArticleSchema(BaseModel):
    """Wrapper for create article request."""

    article: CreateArticleRequestSchema


class UpdateArticleRequestSchema(BaseModel):
    """Request schema for updating an article."""

    title: str | None = None
    description: str | None = None
    body: str | None = None


class UpdateArticleSchema(BaseModel):
    """Wrapper for update article request."""

    article: UpdateArticleRequestSchema


class TagsResponseSchema(BaseModel):
    """Tags response schema."""

    tags: list[str]
