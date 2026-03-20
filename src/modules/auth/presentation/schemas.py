"""Pydantic schemas for auth API."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    name: str
    bio: str | None = None
    image: str | None = None
    created_at: datetime
    updated_at: datetime


class UserResponseWrapper(BaseModel):
    """Wrapper for user response (RealWorld API format)."""

    user: UserResponse


class AuthResponse(BaseModel):
    """Authentication response schema."""

    email: str
    token: str
    name: str
    bio: str | None = None
    image: str | None = None


class AuthResponseWrapper(BaseModel):
    """Wrapper for auth response (RealWorld API format)."""

    user: AuthResponse


class RegisterRequest(BaseModel):
    """Register request schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=60)
    password: str = Field(..., min_length=8)


class RegisterRequestWrapper(BaseModel):
    """Wrapper for register request (RealWorld API format)."""

    user: RegisterRequest


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class LoginRequestWrapper(BaseModel):
    """Wrapper for login request (RealWorld API format)."""

    user: LoginRequest


class UpdateUserRequest(BaseModel):
    """Update user request schema."""

    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=60)
    password: str | None = Field(None, min_length=8)
    bio: str | None = None
    image: str | None = None


class UpdateUserRequestWrapper(BaseModel):
    """Wrapper for update user request (RealWorld API format)."""

    user: UpdateUserRequest
