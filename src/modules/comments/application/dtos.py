"""Data Transfer Objects for comments module."""

from datetime import datetime

from pydantic import BaseModel, Field


class CommentAuthorDTO(BaseModel):
    """DTO for comment author information."""

    name: str
    bio: str | None = None
    image: str | None = None
    following: bool = False


class CommentDTO(BaseModel):
    """DTO for comment data."""

    id: int
    body: str
    created_at: datetime
    updated_at: datetime
    author: CommentAuthorDTO


class CreateCommentRequest(BaseModel):
    """Request DTO for creating a comment."""

    body: str = Field(min_length=1)
    author_id: int
    article_id: int


class ListCommentsRequest(BaseModel):
    """Request DTO for listing comments."""

    article_id: int
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
