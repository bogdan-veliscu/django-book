"""Tests for auth domain entities and value objects."""

import pytest

from src.core.domain.exceptions import ValidationException
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.value_objects import Email, Password


class TestEmail:
    """Tests for Email value object."""

    def test_valid_email(self) -> None:
        """Test creating a valid email."""
        email = Email("test@example.com")
        assert email.value == "test@example.com"

    def test_email_normalization(self) -> None:
        """Test email is normalized to lowercase."""
        email = Email("Test@Example.COM")
        assert email.value == "test@example.com"

    def test_invalid_email_format(self) -> None:
        """Test invalid email format raises exception."""
        with pytest.raises(ValidationException, match="Invalid email format"):
            Email("not-an-email")

    def test_empty_email(self) -> None:
        """Test empty email raises exception."""
        with pytest.raises(ValidationException, match="Email cannot be empty"):
            Email("")

    def test_email_equality(self) -> None:
        """Test email equality."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        email3 = Email("other@example.com")

        assert email1 == email2
        assert email1 != email3


class TestPassword:
    """Tests for Password value object."""

    def test_password_hashing(self) -> None:
        """Test password is hashed."""
        password = Password.from_raw("mysecretpassword")
        assert password.hashed != "mysecretpassword"
        assert password.hashed.startswith("$2b$")  # bcrypt hash

    def test_password_verification(self) -> None:
        """Test password verification."""
        password = Password.from_raw("mysecretpassword")
        assert password.verify("mysecretpassword") is True
        assert password.verify("wrongpassword") is False

    def test_password_min_length(self) -> None:
        """Test password minimum length validation."""
        with pytest.raises(ValidationException, match="at least 8 characters"):
            Password.from_raw("short")

    def test_password_from_hash(self) -> None:
        """Test creating password from hash."""
        raw_password = "mysecretpassword"
        password1 = Password.from_raw(raw_password)
        password2 = Password.from_hash(password1.hashed)

        assert password2.verify(raw_password) is True


class TestUser:
    """Tests for User entity."""

    def test_create_user(self) -> None:
        """Test creating a user."""
        user = User(
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )

        assert user.email.value == "test@example.com"
        assert user.name == "Test User"
        assert user.bio is None
        assert user.image is None

    def test_user_with_optional_fields(self) -> None:
        """Test creating user with optional fields."""
        user = User(
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
            bio="I love coding",
            image="https://example.com/avatar.jpg",
        )

        assert user.bio == "I love coding"
        assert user.image == "https://example.com/avatar.jpg"

    def test_update_user_profile(self) -> None:
        """Test updating user profile."""
        user = User(
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )

        user.update_profile(
            name="Updated Name",
            bio="New bio",
            image="https://example.com/new-avatar.jpg",
        )

        assert user.name == "Updated Name"
        assert user.bio == "New bio"
        assert user.image == "https://example.com/new-avatar.jpg"

    def test_update_password(self) -> None:
        """Test updating user password."""
        user = User(
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )

        old_password_hash = user.password.hashed
        user.update_password(Password.from_raw("newpassword123"))

        assert user.password.hashed != old_password_hash
        assert user.password.verify("newpassword123") is True

    def test_verify_password(self) -> None:
        """Test password verification."""
        user = User(
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )

        assert user.verify_password("password123") is True
        assert user.verify_password("wrongpassword") is False

    def test_user_equality(self) -> None:
        """Test user equality based on ID."""
        user1 = User(
            id=1,
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )
        user2 = User(
            id=1,
            email=Email("other@example.com"),
            name="Other User",
            password=Password.from_raw("password123"),
        )
        user3 = User(
            id=2,
            email=Email("test@example.com"),
            name="Test User",
            password=Password.from_raw("password123"),
        )

        assert user1 == user2  # Same ID
        assert user1 != user3  # Different ID
