"""Data Transfer Objects for auth module."""

from datetime import datetime

from src.core.application.dto import DTO


class UserDTO(DTO):
    """User data transfer object."""

    id: int
    email: str
    name: str
    bio: str | None = None
    image: str | None = None
    created_at: datetime
    updated_at: datetime


class AuthTokenDTO(DTO):
    """Authentication token data transfer object."""

    token: str
    user: UserDTO


class RegisterUserRequest(DTO):
    """Request to register a new user."""

    email: str
    name: str
    password: str


class LoginUserRequest(DTO):
    """Request to login a user."""

    email: str
    password: str


class UpdateUserRequest(DTO):
    """Request to update user profile."""

    email: str | None = None
    name: str | None = None
    bio: str | None = None
    image: str | None = None
    password: str | None = None
