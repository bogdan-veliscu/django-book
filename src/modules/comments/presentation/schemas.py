"""Pydantic schemas for comments API."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileSchema(BaseModel):
    """Profile schema for comment author."""

    username: str
    bio: str | None = None
    image: str | None = None
    following: bool


class CommentSchema(BaseModel):
    """Comment schema for API responses."""

    id: int
    body: str
    createdAt: datetime
    updatedAt: datetime
    author: ProfileSchema


class CommentResponseSchema(BaseModel):
    """Single comment response schema."""

    comment: CommentSchema


class MultipleCommentsResponseSchema(BaseModel):
    """Multiple comments response schema."""

    comments: list[CommentSchema]


class CreateCommentRequestSchema(BaseModel):
    """Request schema for creating a comment."""

    body: str = Field(min_length=1)


class CreateCommentSchema(BaseModel):
    """Wrapper for create comment request."""

    comment: CreateCommentRequestSchema
