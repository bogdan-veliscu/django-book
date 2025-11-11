"""Pydantic schemas for profiles API."""

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    """Profile response schema."""

    name: str
    bio: str | None = None
    image: str | None = None
    following: bool = False


class ProfileResponseWrapper(BaseModel):
    """Wrapper for profile response (RealWorld API format)."""

    profile: ProfileResponse
