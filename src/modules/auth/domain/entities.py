"""Auth domain entities."""

from datetime import datetime

from src.core.domain.entities import TimestampedEntity
from src.modules.auth.domain.value_objects import Email, Password


class User(TimestampedEntity):
    """User entity representing an authenticated user in the system."""

    def __init__(
        self,
        email: Email,
        name: str,
        password: Password,
        id: int | None = None,
        bio: str | None = None,
        image: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize user.

        Args:
            email: User's email address.
            name: User's display name.
            password: User's hashed password.
            id: User's unique identifier.
            bio: User's biography (optional).
            image: User's profile image URL (optional).
            created_at: When the user was created.
            updated_at: When the user was last updated.
        """
        super().__init__(id, created_at, updated_at)
        self._email = email
        self._name = name
        self._password = password
        self._bio = bio
        self._image = image

    @property
    def email(self) -> Email:
        """Get user's email."""
        return self._email

    @property
    def name(self) -> str:
        """Get user's name."""
        return self._name

    @property
    def password(self) -> Password:
        """Get user's password."""
        return self._password

    @property
    def bio(self) -> str | None:
        """Get user's bio."""
        return self._bio

    @property
    def image(self) -> str | None:
        """Get user's image URL."""
        return self._image

    def update_profile(
        self,
        name: str | None = None,
        bio: str | None = None,
        image: str | None = None,
    ) -> None:
        """Update user's profile information.

        Args:
            name: New name (optional).
            bio: New bio (optional).
            image: New image URL (optional).
        """
        if name is not None:
            self._name = name
        if bio is not None:
            self._bio = bio
        if image is not None:
            self._image = image

        self.mark_updated()

    def update_email(self, new_email: Email) -> None:
        """Update user's email address.

        Args:
            new_email: The new email address.
        """
        self._email = new_email
        self.mark_updated()

    def update_password(self, new_password: Password) -> None:
        """Update user's password.

        Args:
            new_password: The new password.
        """
        self._password = new_password
        self.mark_updated()

    def verify_password(self, raw_password: str) -> bool:
        """Verify a password.

        Args:
            raw_password: The plaintext password to verify.

        Returns:
            True if password matches, False otherwise.
        """
        return self._password.verify(raw_password)

    def __repr__(self) -> str:
        """String representation."""
        return f"User(id={self.id}, email={self.email.value}, name={self.name})"
