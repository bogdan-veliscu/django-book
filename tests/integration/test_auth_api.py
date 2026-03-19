"""Integration tests for Auth API endpoints.

This module contains comprehensive integration tests for the authentication
endpoints including registration, login, and getting the current user.

Test scenarios include:
- User registration with valid/invalid data
- User login with valid/invalid credentials
- Getting current user information with various authentication states
"""

import json
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.value_objects import Email, Password
from src.modules.auth.infrastructure.jwt import JWTService


class TestRegisterUser:
    """Tests for POST /api/users (register user endpoint)."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        client: AsyncClient,
        db_session,
    ) -> None:
        """Test successful user registration with valid data.

        Verifies that:
        - Status code is 201 Created
        - Response contains user data with email, name, bio, image
        - Response includes a valid JWT token
        - Response has the correct structure (wrapped in "user" key)
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "newuser@example.com",
                    "name": "New User",
                    "password": "SecurePassword123",
                }
            },
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "user" in data
        user = data["user"]

        # Verify user fields
        assert user["email"] == "newuser@example.com"
        assert user["name"] == "New User"
        assert "token" in user
        assert len(user["token"]) > 0

        # Verify optional fields are present (can be None)
        assert "bio" in user
        assert "image" in user

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test registration fails with duplicate email.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error message indicates entity already exists
        - Response has error structure with "errors" key
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": test_user.email.value,
                    "name": "Another User",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails with invalid email format.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates invalid email format
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "not-a-valid-email",
                    "name": "Test User",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_user_missing_email(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails when email is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "name": "Test User",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_user_missing_name(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails when name is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "newuser@example.com",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_user_missing_password(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails when password is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "newuser@example.com",
                    "name": "Test User",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_user_weak_password_too_short(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails with password shorter than 8 characters.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates password length requirement
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "newuser@example.com",
                    "name": "Test User",
                    "password": "short",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_user_empty_name(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails with empty name string.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates name validation failure
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "newuser@example.com",
                    "name": "",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_user_response_has_token(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that registration response includes a valid JWT token.

        Verifies that:
        - Token is returned in response
        - Token is not empty
        - Token can be parsed (basic JWT format check)
        """
        response = await client.post(
            "/api/users",
            json={
                "user": {
                    "email": "tokentest@example.com",
                    "name": "Token Test",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 201
        data = response.json()
        token = data["user"]["token"]

        # Verify token has JWT format (3 parts separated by dots)
        assert token.count(".") == 2, "Token should be in JWT format with 3 parts"

    @pytest.mark.asyncio
    async def test_register_user_invalid_request_body(
        self,
        client: AsyncClient,
    ) -> None:
        """Test registration fails with malformed request body.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Request missing the required "user" wrapper key fails
        """
        response = await client.post(
            "/api/users",
            json={
                "email": "newuser@example.com",
                "name": "Test User",
                "password": "ValidPassword123",
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


class TestLoginUser:
    """Tests for POST /api/users/login (login user endpoint)."""

    @pytest.mark.asyncio
    async def test_login_user_success(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful user login with valid credentials.

        Verifies that:
        - Status code is 200 OK
        - Response contains user data with email and name
        - Response includes a valid JWT token
        - Response has the correct structure (wrapped in "user" key)
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": test_user.email.value,
                    "password": "password123",
                }
            },
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "user" in data
        user = data["user"]

        # Verify user fields
        assert user["email"] == test_user.email.value
        assert user["name"] == test_user.name
        assert "token" in user
        assert len(user["token"]) > 0

    @pytest.mark.asyncio
    async def test_login_user_invalid_email(
        self,
        client: AsyncClient,
    ) -> None:
        """Test login fails with non-existent user email.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error message indicates invalid credentials
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": "nonexistent@example.com",
                    "password": "SomePassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        data = response.json()
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_login_user_invalid_password(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test login fails with incorrect password.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error message indicates invalid credentials
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": test_user.email.value,
                    "password": "WrongPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        data = response.json()
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_login_user_missing_email(
        self,
        client: AsyncClient,
    ) -> None:
        """Test login fails when email is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "password": "SomePassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_login_user_missing_password(
        self,
        client: AsyncClient,
    ) -> None:
        """Test login fails when password is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": "test@example.com",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_login_user_invalid_email_format(
        self,
        client: AsyncClient,
    ) -> None:
        """Test login fails with invalid email format.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates invalid email format
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": "not-a-valid-email",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_login_user_invalid_request_body(
        self,
        client: AsyncClient,
    ) -> None:
        """Test login fails with malformed request body.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Request missing the required "user" wrapper key fails
        """
        response = await client.post(
            "/api/users/login",
            json={
                "email": "test@example.com",
                "password": "ValidPassword123",
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_login_user_empty_email(
        self,
        client: AsyncClient,
    ) -> None:
        """Test login fails with empty email string.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation failure
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": "",
                    "password": "ValidPassword123",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_login_user_returns_valid_token(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that login response includes a valid JWT token.

        Verifies that:
        - Token is returned in response
        - Token is not empty
        - Token can be parsed (basic JWT format check)
        """
        response = await client.post(
            "/api/users/login",
            json={
                "user": {
                    "email": test_user.email.value,
                    "password": "password123",
                }
            },
        )

        assert response.status_code == 200
        data = response.json()
        token = data["user"]["token"]

        # Verify token has JWT format (3 parts separated by dots)
        assert token.count(".") == 2, "Token should be in JWT format with 3 parts"


class TestGetCurrentUser:
    """Tests for GET /api/user (get current user endpoint)."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successfully retrieving current authenticated user.

        Verifies that:
        - Status code is 200 OK
        - Response contains all user fields (id, email, name, bio, image)
        - Response includes timestamps (created_at, updated_at)
        - Response has the correct structure (wrapped in "user" key)
        """
        response = await authenticated_client.get("/api/user")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "user" in data
        user = data["user"]

        # Verify all user fields
        assert user["id"] is not None
        assert user["email"] == test_user.email.value
        assert user["name"] == test_user.name
        assert "bio" in user
        assert "image" in user
        assert "created_at" in user
        assert "updated_at" in user

        # Verify timestamps are valid ISO format
        assert isinstance(user["created_at"], str)
        assert isinstance(user["updated_at"], str)

    @pytest.mark.asyncio
    async def test_get_current_user_missing_authorization_header(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that missing authorization header returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing authorization header
        """
        response = await client.get("/api/user")

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that invalid token returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates invalid or malformed token
        """
        response = await client.get(
            "/api/user",
            headers={"Authorization": "Token invalid.token.here"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_token_in_header(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that malformed authorization header returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates invalid header format
        """
        response = await client.get(
            "/api/user",
            headers={"Authorization": "Bearer some_token"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(
        self,
        client: AsyncClient,
        test_settings,
    ) -> None:
        """Test that expired token returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates expired token
        """
        from jose import jwt as jose_jwt

        # Create an expired token manually
        now = datetime.now(timezone.utc)
        expired_payload = {
            "sub": "999",
            "email": "test@example.com",
            "iat": now,
            "exp": now - timedelta(seconds=3600),  # Expired 1 hour ago
        }
        expired_token = jose_jwt.encode(
            expired_payload,
            test_settings.secret_key,
            algorithm=test_settings.algorithm,
        )

        response = await client.get(
            "/api/user",
            headers={"Authorization": f"Token {expired_token}"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_malformed_authorization_header_no_token(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that authorization header without token returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates invalid header format
        """
        response = await client.get(
            "/api/user",
            headers={"Authorization": "Token"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_case_insensitive_token_prefix(
        self,
        client: AsyncClient,
        test_user: User,
        test_user_token: str,
    ) -> None:
        """Test that Token prefix is case-insensitive.

        Verifies that:
        - Authorization header with lowercase "token" works
        - Status code is 200 OK
        """
        # Test with lowercase "token"
        response = await client.get(
            "/api/user",
            headers={"Authorization": f"token {test_user_token}"},
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_empty_authorization_header(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that empty authorization header returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing or invalid header
        """
        response = await client.get(
            "/api/user",
            headers={"Authorization": ""},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_second_user(
        self,
        authenticated_client2: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that authenticated user gets their own data (not another user's).

        Verifies that:
        - Status code is 200 OK
        - Response contains the authenticated user's data
        - Response does not contain other user's data
        """
        response = await authenticated_client2.get("/api/user")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify we get the correct user's data
        assert data["user"]["email"] == test_user2.email.value
        assert data["user"]["name"] == test_user2.name

    @pytest.mark.asyncio
    async def test_get_current_user_response_format(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that response has correct JSON structure and field types.

        Verifies that:
        - id is an integer
        - email is a string
        - name is a string
        - bio is string or null
        - image is string or null
        - created_at and updated_at are ISO format strings
        """
        response = await authenticated_client.get("/api/user")

        assert response.status_code == 200
        data = response.json()
        user = data["user"]

        # Verify field types
        assert isinstance(user["id"], int)
        assert isinstance(user["email"], str)
        assert isinstance(user["name"], str)
        assert user["bio"] is None or isinstance(user["bio"], str)
        assert user["image"] is None or isinstance(user["image"], str)
        assert isinstance(user["created_at"], str)
        assert isinstance(user["updated_at"], str)

    @pytest.mark.asyncio
    async def test_get_current_user_with_special_characters_in_token(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that token with special characters (but invalid JWT) returns 401.

        Verifies that:
        - Status code is 401 Unauthorized
        - Invalid tokens are properly rejected
        """
        response = await client.get(
            "/api/user",
            headers={"Authorization": "Token abc!@#$%^&*().xyz.123"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_current_user_multiple_requests_same_token(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that the same token works for multiple requests.

        Verifies that:
        - Multiple requests with same token all succeed
        - Status code is 200 OK for all requests
        - All responses contain the same user data
        """
        for _ in range(3):
            response = await authenticated_client.get("/api/user")
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["email"] == test_user.email.value


class TestUpdateCurrentUser:
    """Tests for PUT /api/user (update current user endpoint)."""

    @pytest.mark.asyncio
    async def test_update_user_bio(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test updating user bio."""
        response = await authenticated_client.put(
            "/api/user",
            json={"user": {"bio": "I love writing articles"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["bio"] == "I love writing articles"
        assert data["user"]["email"] == test_user.email.value

    @pytest.mark.asyncio
    async def test_update_user_image(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test updating user image URL."""
        response = await authenticated_client.put(
            "/api/user",
            json={"user": {"image": "https://example.com/avatar.png"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["image"] == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_update_user_name(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test updating username."""
        response = await authenticated_client.put(
            "/api/user",
            json={"user": {"name": "updatedusername"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "updatedusername"

    @pytest.mark.asyncio
    async def test_update_user_email(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test updating user email address."""
        response = await authenticated_client.put(
            "/api/user",
            json={"user": {"email": "newemail@example.com"}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_update_user_password(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
        client: AsyncClient,
    ) -> None:
        """Test that password can be changed and new password works for login."""
        response = await authenticated_client.put(
            "/api/user",
            json={"user": {"password": "NewPassword456"}},
        )
        assert response.status_code == 200

        # Verify new password works
        login_response = await client.post(
            "/api/users/login",
            json={"user": {"email": test_user.email.value, "password": "NewPassword456"}},
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_user_multiple_fields(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test updating multiple fields at once."""
        response = await authenticated_client.put(
            "/api/user",
            json={
                "user": {
                    "bio": "Updated bio",
                    "image": "https://example.com/new-avatar.png",
                    "name": "updatedname",
                }
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["bio"] == "Updated bio"
        assert data["user"]["image"] == "https://example.com/new-avatar.png"
        assert data["user"]["name"] == "updatedname"

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(
        self,
        authenticated_client: AsyncClient,
        client: AsyncClient,
        db_session,
    ) -> None:
        """Test that updating to an email already taken returns 422."""
        # Create another user
        await client.post(
            "/api/users",
            json={"user": {"email": "other@example.com", "name": "otheruser", "password": "Password123"}},
        )

        response = await authenticated_client.put(
            "/api/user",
            json={"user": {"email": "other@example.com"}},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_user_requires_auth(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that unauthenticated requests are rejected."""
        response = await client.put(
            "/api/user",
            json={"user": {"bio": "test"}},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_empty_body(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that an empty update returns the unchanged user."""
        response = await authenticated_client.put(
            "/api/user",
            json={"user": {}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == test_user.email.value
