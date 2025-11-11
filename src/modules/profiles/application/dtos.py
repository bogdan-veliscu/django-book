"""Data Transfer Objects for profiles module."""

from src.core.application.dto import DTO


class ProfileDTO(DTO):
    """Profile data transfer object."""

    user_id: int
    email: str
    name: str
    bio: str | None = None
    image: str | None = None
    following: bool = False  # Is the current user following this profile?


class GetProfileRequest(DTO):
    """Request to get a profile by name."""

    name: str
    current_user_id: int | None = None  # For checking if current user follows


class FollowUserRequest(DTO):
    """Request to follow a user."""

    follower_id: int  # The user doing the following
    followee_name: str  # The name of the user to follow


class UnfollowUserRequest(DTO):
    """Request to unfollow a user."""

    follower_id: int  # The user doing the unfollowing
    followee_name: str  # The name of the user to unfollow
