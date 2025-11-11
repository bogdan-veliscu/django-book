"""Auth domain value objects."""

import re

import bcrypt

from src.core.domain.exceptions import ValidationException
from src.core.domain.value_objects import ValueObject

# Email validation regex
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class Email(ValueObject):
    """Email value object."""

    def __init__(self, value: str) -> None:
        """Initialize email.

        Args:
            value: The email address.

        Raises:
            ValidationException: If email is invalid.
        """
        if not value or not value.strip():
            raise ValidationException("Email cannot be empty", field="email")

        value = value.strip().lower()

        if not EMAIL_REGEX.match(value):
            raise ValidationException("Invalid email format", field="email")

        self._value = value

    @property
    def value(self) -> str:
        """Get the email value."""
        return self._value

    def __str__(self) -> str:
        """String representation."""
        return self._value


class Password(ValueObject):
    """Password value object.

    Passwords are always stored hashed. Use from_raw() to create from plaintext.
    """

    MIN_LENGTH = 8

    def __init__(self, hashed: str) -> None:
        """Initialize password with hashed value.

        Args:
            hashed: The hashed password.
        """
        self._hashed = hashed

    @classmethod
    def from_raw(cls, raw_password: str) -> "Password":
        """Create password from raw (plaintext) password.

        Args:
            raw_password: The plaintext password.

        Returns:
            A new Password instance with hashed password.

        Raises:
            ValidationException: If password is invalid.
        """
        if len(raw_password) < cls.MIN_LENGTH:
            raise ValidationException(
                f"Password must be at least {cls.MIN_LENGTH} characters long",
                field="password",
            )

        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
        hashed = hashed_bytes.decode("utf-8")
        return cls(hashed)

    @classmethod
    def from_hash(cls, hashed: str) -> "Password":
        """Create password from already hashed value.

        Args:
            hashed: The hashed password.

        Returns:
            A new Password instance.
        """
        return cls(hashed)

    @property
    def hashed(self) -> str:
        """Get the hashed password."""
        return self._hashed

    def verify(self, raw_password: str) -> bool:
        """Verify a raw password against the hash.

        Args:
            raw_password: The plaintext password to verify.

        Returns:
            True if password matches, False otherwise.
        """
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            self._hashed.encode("utf-8"),
        )

    def __str__(self) -> str:
        """String representation."""
        return "********"  # Never expose the hash
