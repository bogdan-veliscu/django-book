"""Integration tests for Profiles API endpoints.

This module contains comprehensive integration tests for the profiles
endpoints including getting user profiles, following, and unfollowing users.

Test scenarios include:
- Getting user profiles with and without authentication
- Following and unfollowing users
- Error handling for non-existent users
- Self-follow prevention
- Idempotent follow/unfollow operations
- Authentication requirements
"""

import pytest
from httpx import AsyncClient

from src.modules.auth.domain.entities import User


class TestGetProfile:
    """Tests for GET /api/profiles/{name} (get user profile endpoint)."""

    @pytest.mark.asyncio
    async def test_get_profile_success_without_auth(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successfully retrieving a user profile without authentication.

        Verifies that:
        - Status code is 200 OK
        - Response contains profile data with name, bio, image
        - Response has following=false when not authenticated
        - Response has the correct structure (wrapped in "profile" key)
        """
        response = await client.get(f"/api/profiles/{test_user.name}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "profile" in data
        profile = data["profile"]

        # Verify profile fields
        assert profile["name"] == test_user.name
        assert "bio" in profile
        assert "image" in profile
        assert "following" in profile

        # Verify following is false when not authenticated
        assert profile["following"] is False

    @pytest.mark.asyncio
    async def test_get_profile_success_with_auth_not_following(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test retrieving a user profile with authentication but not following.

        Verifies that:
        - Status code is 200 OK
        - Response contains profile data
        - Response has following=false when not following the user
        - Authenticated user can view other profiles
        """
        response = await authenticated_client.get(f"/api/profiles/{test_user2.name}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "profile" in data
        profile = data["profile"]

        # Verify profile fields
        assert profile["name"] == test_user2.name
        assert "bio" in profile
        assert "image" in profile

        # Verify following is false when not following
        assert profile["following"] is False

    @pytest.mark.asyncio
    async def test_get_profile_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that retrieving non-existent profile returns 404 Not Found.

        Verifies that:
        - Status code is 404 Not Found
        - Error message indicates entity not found
        """
        response = await client.get("/api/profiles/nonexistent-user")

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_get_profile_response_structure(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that profile response has correct JSON structure and field types.

        Verifies that:
        - name is a string
        - bio is string or null
        - image is string or null
        - following is a boolean
        """
        response = await authenticated_client.get(f"/api/profiles/{test_user2.name}")

        assert response.status_code == 200
        data = response.json()
        profile = data["profile"]

        # Verify field types
        assert isinstance(profile["name"], str)
        assert profile["bio"] is None or isinstance(profile["bio"], str)
        assert profile["image"] is None or isinstance(profile["image"], str)
        assert isinstance(profile["following"], bool)

    @pytest.mark.asyncio
    async def test_get_profile_following_status_true(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
        test_user: User,
        test_user2: User,
    ) -> None:
        """Test that following status is true after following a user.

        Verifies that:
        - User 1 follows User 2
        - When User 1 retrieves User 2's profile, following=true
        - When User 2 retrieves User 1's profile, following=false (not following back)
        """
        # User 1 follows User 2
        follow_response = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert follow_response.status_code == 200

        # User 1 retrieves User 2's profile
        profile_response = await authenticated_client.get(f"/api/profiles/{test_user2.name}")
        assert profile_response.status_code == 200
        profile = profile_response.json()["profile"]
        assert profile["following"] is True

        # User 2 retrieves User 1's profile (not following back)
        other_profile_response = await authenticated_client2.get(f"/api/profiles/{test_user.name}")
        assert other_profile_response.status_code == 200
        other_profile = other_profile_response.json()["profile"]
        assert other_profile["following"] is False

    @pytest.mark.asyncio
    async def test_get_profile_multiple_fields_present(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that all required profile fields are present in response.

        Verifies that:
        - Response includes name, bio, image, and following fields
        - All fields are accessible
        """
        response = await client.get(f"/api/profiles/{test_user.name}")

        assert response.status_code == 200
        data = response.json()
        profile = data["profile"]

        # Verify all required fields are present
        required_fields = ["name", "bio", "image", "following"]
        for field in required_fields:
            assert field in profile, f"Field '{field}' missing from response"

    @pytest.mark.asyncio
    async def test_get_profile_case_sensitivity(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test profile retrieval with different name cases.

        Verifies that:
        - Profile is retrievable by exact name
        - Returns 404 for incorrect case if system is case-sensitive
        """
        # Get with exact name
        response = await client.get(f"/api/profiles/{test_user.name}")
        assert response.status_code == 200

        # Try with different case (may return 404 if case-sensitive)
        response_different_case = await client.get(
            f"/api/profiles/{test_user.name.upper()}"
        )
        # This depends on system implementation - document behavior
        assert response_different_case.status_code in [200, 404]


class TestFollowUser:
    """Tests for POST /api/profiles/{name}/follow (follow user endpoint)."""

    @pytest.mark.asyncio
    async def test_follow_user_success(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test successfully following a user.

        Verifies that:
        - Status code is 200 OK
        - Response contains the followed user's profile
        - Response has following=true
        - Response has the correct structure (wrapped in "profile" key)
        """
        response = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "profile" in data
        profile = data["profile"]

        # Verify profile fields
        assert profile["name"] == test_user2.name
        assert "bio" in profile
        assert "image" in profile

        # Verify following is true
        assert profile["following"] is True

    @pytest.mark.asyncio
    async def test_follow_user_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that following non-existent user returns 404 Not Found.

        Verifies that:
        - Status code is 404 Not Found
        - Error message indicates entity not found
        """
        response = await authenticated_client.post(
            "/api/profiles/nonexistent-user/follow"
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_follow_user_self_follow_prevention(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that users cannot follow themselves.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation error or domain error
        - Response has error structure
        """
        response = await authenticated_client.post(
            f"/api/profiles/{test_user.name}/follow"
        )

        # Should either be 422 (validation error) or 400 (domain error)
        assert response.status_code in [
            400,
            422,
        ], f"Expected 400 or 422, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_follow_user_already_following_idempotent(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that following an already followed user is idempotent.

        Verifies that:
        - First follow returns 200 OK
        - Second follow also returns 200 OK
        - Both responses have following=true
        - No error is raised
        """
        # First follow
        response1 = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert response1.status_code == 200, f"Expected 200, got {response1.status_code}"
        data1 = response1.json()
        assert data1["profile"]["following"] is True

        # Second follow (should be idempotent)
        response2 = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
        data2 = response2.json()
        assert data2["profile"]["following"] is True

    @pytest.mark.asyncio
    async def test_follow_user_missing_authentication(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that following without authentication returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing or invalid authentication
        """
        response = await client.post(f"/api/profiles/{test_user.name}/follow")

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_follow_user_invalid_token(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that following with invalid token returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Invalid tokens are properly rejected
        """
        response = await client.post(
            f"/api/profiles/{test_user.name}/follow",
            headers={"Authorization": "Token invalid.token.here"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_follow_user_response_structure(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that follow response has correct JSON structure and field types.

        Verifies that:
        - name is a string
        - bio is string or null
        - image is string or null
        - following is a boolean (should be true)
        """
        response = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )

        assert response.status_code == 200
        data = response.json()
        profile = data["profile"]

        # Verify field types
        assert isinstance(profile["name"], str)
        assert profile["bio"] is None or isinstance(profile["bio"], str)
        assert profile["image"] is None or isinstance(profile["image"], str)
        assert isinstance(profile["following"], bool)
        assert profile["following"] is True

    @pytest.mark.asyncio
    async def test_follow_user_multiple_times_by_different_users(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
        test_user: User,
        test_user2: User,
    ) -> None:
        """Test that multiple users can follow the same user.

        Verifies that:
        - User 1 can follow User 2
        - User 2 can also follow User 1
        - Both follow operations succeed
        - Both users show following=true for their respective profiles
        """
        # User 1 follows User 2
        response1 = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert response1.status_code == 200
        assert response1.json()["profile"]["following"] is True

        # User 2 follows User 1
        response2 = await authenticated_client2.post(
            f"/api/profiles/{test_user.name}/follow"
        )
        assert response2.status_code == 200
        assert response2.json()["profile"]["following"] is True

        # Verify User 1 still following User 2
        verify_response1 = await authenticated_client.get(
            f"/api/profiles/{test_user2.name}"
        )
        assert verify_response1.json()["profile"]["following"] is True

        # Verify User 2 still following User 1
        verify_response2 = await authenticated_client2.get(
            f"/api/profiles/{test_user.name}"
        )
        assert verify_response2.json()["profile"]["following"] is True


class TestUnfollowUser:
    """Tests for DELETE /api/profiles/{name}/follow (unfollow user endpoint)."""

    @pytest.mark.asyncio
    async def test_unfollow_user_success(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test successfully unfollowing a user.

        Verifies that:
        - Status code is 200 OK
        - User is first followed (precondition)
        - After unfollowing, response has following=false
        - Response has the correct structure (wrapped in "profile" key)
        """
        # First, follow the user
        follow_response = await authenticated_client.post(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert follow_response.status_code == 200
        assert follow_response.json()["profile"]["following"] is True

        # Now unfollow
        response = await authenticated_client.delete(
            f"/api/profiles/{test_user2.name}/follow"
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "profile" in data
        profile = data["profile"]

        # Verify profile fields
        assert profile["name"] == test_user2.name
        assert "bio" in profile
        assert "image" in profile

        # Verify following is false after unfollow
        assert profile["following"] is False

    @pytest.mark.asyncio
    async def test_unfollow_user_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that unfollowing non-existent user returns 404 Not Found.

        Verifies that:
        - Status code is 404 Not Found
        - Error message indicates entity not found
        """
        response = await authenticated_client.delete(
            "/api/profiles/nonexistent-user/follow"
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "errors" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_unfollow_user_not_following_idempotent(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that unfollowing a user you're not following is idempotent.

        Verifies that:
        - Unfollowing without prior follow returns 200 OK
        - Response has following=false
        - No error is raised
        """
        # Unfollow without prior follow
        response = await authenticated_client.delete(
            f"/api/profiles/{test_user2.name}/follow"
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["profile"]["following"] is False

    @pytest.mark.asyncio
    async def test_unfollow_user_twice_idempotent(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that unfollowing twice is idempotent.

        Verifies that:
        - First unfollow returns 200 OK
        - Second unfollow also returns 200 OK
        - Both responses have following=false
        - No error is raised
        """
        # Follow first
        await authenticated_client.post(f"/api/profiles/{test_user2.name}/follow")

        # First unfollow
        response1 = await authenticated_client.delete(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert response1.status_code == 200, f"Expected 200, got {response1.status_code}"
        data1 = response1.json()
        assert data1["profile"]["following"] is False

        # Second unfollow (should be idempotent)
        response2 = await authenticated_client.delete(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert response2.status_code == 200, f"Expected 200, got {response2.status_code}"
        data2 = response2.json()
        assert data2["profile"]["following"] is False

    @pytest.mark.asyncio
    async def test_unfollow_user_missing_authentication(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that unfollowing without authentication returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing or invalid authentication
        """
        response = await client.delete(f"/api/profiles/{test_user.name}/follow")

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_unfollow_user_invalid_token(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test that unfollowing with invalid token returns 401 Unauthorized.

        Verifies that:
        - Status code is 401 Unauthorized
        - Invalid tokens are properly rejected
        """
        response = await client.delete(
            f"/api/profiles/{test_user.name}/follow",
            headers={"Authorization": "Token invalid.token.here"},
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_unfollow_user_response_structure(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that unfollow response has correct JSON structure and field types.

        Verifies that:
        - name is a string
        - bio is string or null
        - image is string or null
        - following is a boolean (should be false)
        """
        # Follow first to ensure we're unfollowing
        await authenticated_client.post(f"/api/profiles/{test_user2.name}/follow")

        # Then unfollow
        response = await authenticated_client.delete(
            f"/api/profiles/{test_user2.name}/follow"
        )

        assert response.status_code == 200
        data = response.json()
        profile = data["profile"]

        # Verify field types
        assert isinstance(profile["name"], str)
        assert profile["bio"] is None or isinstance(profile["bio"], str)
        assert profile["image"] is None or isinstance(profile["image"], str)
        assert isinstance(profile["following"], bool)
        assert profile["following"] is False

    @pytest.mark.asyncio
    async def test_unfollow_after_follow_persistence(
        self,
        authenticated_client: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test that follow/unfollow state changes persist.

        Verifies that:
        - After following, get profile shows following=true
        - After unfollowing, get profile shows following=false
        - State changes are reflected in subsequent requests
        """
        # Follow
        await authenticated_client.post(f"/api/profiles/{test_user2.name}/follow")
        get_response1 = await authenticated_client.get(f"/api/profiles/{test_user2.name}")
        assert get_response1.json()["profile"]["following"] is True

        # Unfollow
        await authenticated_client.delete(f"/api/profiles/{test_user2.name}/follow")
        get_response2 = await authenticated_client.get(f"/api/profiles/{test_user2.name}")
        assert get_response2.json()["profile"]["following"] is False

    @pytest.mark.asyncio
    async def test_unfollow_mutual_follows_independent(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
        test_user: User,
        test_user2: User,
    ) -> None:
        """Test that unfollowing one user doesn't affect other follow relationships.

        Verifies that:
        - User 1 follows User 2
        - User 2 follows User 1
        - User 1 unfollows User 2
        - User 2 still follows User 1
        - Both users can still see each other's profiles
        """
        # User 1 follows User 2
        await authenticated_client.post(f"/api/profiles/{test_user2.name}/follow")

        # User 2 follows User 1
        await authenticated_client2.post(f"/api/profiles/{test_user.name}/follow")

        # User 1 unfollows User 2
        response = await authenticated_client.delete(
            f"/api/profiles/{test_user2.name}/follow"
        )
        assert response.status_code == 200
        assert response.json()["profile"]["following"] is False

        # Verify User 1 is no longer following User 2
        verify_response1 = await authenticated_client.get(
            f"/api/profiles/{test_user2.name}"
        )
        assert verify_response1.json()["profile"]["following"] is False

        # Verify User 2 still follows User 1
        verify_response2 = await authenticated_client2.get(
            f"/api/profiles/{test_user.name}"
        )
        assert verify_response2.json()["profile"]["following"] is True
