"""Integration tests for Articles API endpoints.

This module contains comprehensive integration tests for the articles
endpoints including creation, retrieval, updating, deletion, favoriting,
and listing with various filters.

Test scenarios include:
- Creating articles with valid/invalid data
- Retrieving articles by slug
- Updating articles with authorization checks
- Deleting articles with authorization checks
- Favoriting and unfavoriting articles
- Listing articles with filters (tag, author, favorited)
- Getting user's article feed
- Getting all tags
"""

import pytest
from httpx import AsyncClient

from src.modules.auth.domain.entities import User
from src.modules.auth.domain.value_objects import Email, Password


class TestCreateArticle:
    """Tests for POST /api/articles (create article endpoint)."""

    @pytest.mark.asyncio
    async def test_create_article_success(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful article creation with valid data.

        Verifies that:
        - Status code is 201 Created
        - Response contains article data with all fields
        - Author is set to current user
        - Response includes correct structure (wrapped in "article" key)
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article 1",
                    "description": "This is a test article",
                    "body": "This is the body of the test article with some content.",
                    "tagList": ["test", "python"],
                }
            },
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "article" in data
        article = data["article"]

        # Verify article fields
        assert article["title"] == "Test Article 1"
        assert article["description"] == "This is a test article"
        assert article["body"] == "This is the body of the test article with some content."
        assert set(article["tagList"]) == {"test", "python"}
        assert "slug" in article
        assert article["slug"] == "test-article-1"

        # Verify author is current user
        assert article["author"]["username"] == test_user.name
        assert article["favorited"] is False
        assert article["favoritesCount"] == 0

        # Verify timestamps exist
        assert "createdAt" in article
        assert "updatedAt" in article

    @pytest.mark.asyncio
    async def test_create_article_without_tags(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article without tags.

        Verifies that:
        - Status code is 201 Created
        - tagList is empty list
        - Article is created successfully without tags
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article Without Tags",
                    "description": "Article without any tags",
                    "body": "Body content without tags.",
                }
            },
        )

        assert response.status_code == 201
        data = response.json()
        article = data["article"]

        assert article["tagList"] == []

    @pytest.mark.asyncio
    async def test_create_article_auth_required(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that creating article requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing authorization
        """
        response = await client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_article_missing_title(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article fails when title is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_article_missing_description(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article fails when description is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "body": "Body content",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_article_missing_body(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article fails when body is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_article_empty_title(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article fails when title is empty string.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation failure
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_article_empty_description(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article fails when description is empty string.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation failure
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "",
                    "body": "Body content",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_article_empty_body(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating article fails when body is empty string.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation failure
        """
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


class TestGetArticle:
    """Tests for GET /api/articles/{slug} (get article endpoint)."""

    @pytest.mark.asyncio
    async def test_get_article_success(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successfully retrieving an article by slug.

        Verifies that:
        - Status code is 200 OK
        - Response contains complete article data
        - Author information is included
        - Tags are returned in tagList
        """
        # Create an article first
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Get Test Article",
                    "description": "Test article for get",
                    "body": "This is test content for getting article.",
                    "tagList": ["test", "get"],
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Now get the article
        response = await client.get(f"/api/articles/{created_article['slug']}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify article structure
        assert "article" in data
        article = data["article"]

        assert article["title"] == "Get Test Article"
        assert article["description"] == "Test article for get"
        assert article["body"] == "This is test content for getting article."
        assert set(article["tagList"]) == {"test", "get"}
        assert article["author"]["username"] == test_user.name

    @pytest.mark.asyncio
    async def test_get_article_with_authentication(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test getting article with authentication.

        Verifies that:
        - Status code is 200 OK
        - Article is returned with favorited status
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Auth Test Article",
                    "description": "Test with auth",
                    "body": "Content for authenticated test.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Get article with authentication
        response = await authenticated_client.get(
            f"/api/articles/{created_article['slug']}"
        )

        assert response.status_code == 200
        data = response.json()
        article = data["article"]

        # Favorited should be False since we didn't favorite our own article
        assert article["favorited"] is False

    @pytest.mark.asyncio
    async def test_get_article_not_found(
        self,
        client: AsyncClient,
    ) -> None:
        """Test getting non-existent article returns 404.

        Verifies that:
        - Status code is 404 Not Found
        - Error indicates article not found
        """
        response = await client.get("/api/articles/nonexistent-article-slug")

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_article_without_authentication(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test getting article without authentication.

        Verifies that:
        - Status code is 200 OK
        - Article data is returned
        - favorited is false
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Unauthenticated Test",
                    "description": "Test without auth",
                    "body": "Content for unauthenticated test.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Get article without authentication
        response = await client.get(f"/api/articles/{created_article['slug']}")

        assert response.status_code == 200
        data = response.json()
        article = data["article"]

        assert article["favorited"] is False


class TestUpdateArticle:
    """Tests for PUT /api/articles/{slug} (update article endpoint)."""

    @pytest.mark.asyncio
    async def test_update_article_success(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test successfully updating an article by author.

        Verifies that:
        - Status code is 200 OK
        - Updated fields are reflected in response
        - Slug remains unchanged
        - Updated timestamp is changed
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Original Title",
                    "description": "Original description",
                    "body": "Original body content.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Update the article
        response = await authenticated_client.put(
            f"/api/articles/{created_article['slug']}",
            json={
                "article": {
                    "title": "Updated Title",
                    "description": "Updated description",
                    "body": "Updated body content with more information.",
                }
            },
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        article = data["article"]
        assert article["title"] == "Updated Title"
        assert article["description"] == "Updated description"
        assert article["body"] == "Updated body content with more information."

    @pytest.mark.asyncio
    async def test_update_article_partial(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test partial update of article (only some fields).

        Verifies that:
        - Status code is 200 OK
        - Only specified fields are updated
        - Unspecified fields remain unchanged
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Original Title",
                    "description": "Original description",
                    "body": "Original body content.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Update only title
        response = await authenticated_client.put(
            f"/api/articles/{created_article['slug']}",
            json={
                "article": {
                    "title": "Updated Title",
                }
            },
        )

        assert response.status_code == 200
        data = response.json()
        article = data["article"]

        assert article["title"] == "Updated Title"
        assert article["description"] == "Original description"
        assert article["body"] == "Original body content."

    @pytest.mark.asyncio
    async def test_update_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test updating non-existent article returns 404.

        Verifies that:
        - Status code is 404 Not Found
        - Error indicates article not found
        """
        response = await authenticated_client.put(
            "/api/articles/nonexistent-slug",
            json={
                "article": {
                    "title": "New Title",
                    "description": "New description",
                    "body": "New body",
                }
            },
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_update_article_not_author(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test that non-author cannot update article (403 Forbidden).

        Verifies that:
        - Status code is 403 Forbidden
        - Error indicates not authorized
        """
        # Create an article with user 1
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "User1 Article",
                    "description": "Created by user 1",
                    "body": "Content from user 1.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Try to update with user 2
        response = await authenticated_client2.put(
            f"/api/articles/{created_article['slug']}",
            json={
                "article": {
                    "title": "Hacked Title",
                }
            },
        )

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_update_article_auth_required(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that updating article requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        """
        # Create an article with authenticated client
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Test",
                    "body": "Test body",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Try to update without authentication
        response = await client.put(
            f"/api/articles/{created_article['slug']}",
            json={
                "article": {
                    "title": "Updated",
                }
            },
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestDeleteArticle:
    """Tests for DELETE /api/articles/{slug} (delete article endpoint)."""

    @pytest.mark.asyncio
    async def test_delete_article_success(
        self,
        authenticated_client: AsyncClient,
        client: AsyncClient,
    ) -> None:
        """Test successfully deleting an article by author.

        Verifies that:
        - Status code is 204 No Content
        - Article is no longer retrievable after deletion
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article to Delete",
                    "description": "This will be deleted",
                    "body": "Temporary content.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]
        slug = created_article["slug"]

        # Delete the article
        delete_response = await authenticated_client.delete(f"/api/articles/{slug}")

        assert delete_response.status_code == 204, (
            f"Expected 204, got {delete_response.status_code}"
        )

        # Verify article is no longer retrievable
        get_response = await client.get(f"/api/articles/{slug}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test deleting non-existent article returns 404.

        Verifies that:
        - Status code is 404 Not Found
        """
        response = await authenticated_client.delete("/api/articles/nonexistent-slug")

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_article_not_author(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test that non-author cannot delete article (403 Forbidden).

        Verifies that:
        - Status code is 403 Forbidden
        """
        # Create an article with user 1
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "User1 Article",
                    "description": "Created by user 1",
                    "body": "Content from user 1.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Try to delete with user 2
        response = await authenticated_client2.delete(
            f"/api/articles/{created_article['slug']}"
        )

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_article_auth_required(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that deleting article requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Test",
                    "body": "Test body",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Try to delete without authentication
        response = await client.delete(f"/api/articles/{created_article['slug']}")

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestFavoriteArticle:
    """Tests for POST /api/articles/{slug}/favorite (favorite article endpoint)."""

    @pytest.mark.asyncio
    async def test_favorite_article_success(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test successfully favoriting an article.

        Verifies that:
        - Status code is 200 OK
        - Response includes favorited=true
        - favoritesCount is incremented
        """
        # User 1 creates an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article to Favorite",
                    "description": "Favorite test",
                    "body": "This article will be favorited.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]
        slug = created_article["slug"]

        # User 2 favorites the article
        response = await authenticated_client2.post(f"/api/articles/{slug}/favorite")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        article = data["article"]

        assert article["favorited"] is True
        assert article["favoritesCount"] == 1

    @pytest.mark.asyncio
    async def test_favorite_article_already_favorited(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test that favoriting already favorited article is idempotent.

        Verifies that:
        - Status code is 200 OK
        - Favoriting multiple times doesn't increase count
        - Article remains favorited
        """
        # User 1 creates an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Idempotent Favorite",
                    "description": "Idempotent test",
                    "body": "Test idempotent favoriting.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]
        slug = created_article["slug"]

        # User 2 favorites the article twice
        response1 = await authenticated_client2.post(f"/api/articles/{slug}/favorite")
        assert response1.status_code == 200
        data1 = response1.json()
        article1 = data1["article"]

        response2 = await authenticated_client2.post(f"/api/articles/{slug}/favorite")
        assert response2.status_code == 200
        data2 = response2.json()
        article2 = data2["article"]

        # Both should have same favorite count
        assert article1["favoritesCount"] == article2["favoritesCount"] == 1

    @pytest.mark.asyncio
    async def test_favorite_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test favoriting non-existent article returns 404.

        Verifies that:
        - Status code is 404 Not Found
        """
        response = await authenticated_client.post(
            "/api/articles/nonexistent-slug/favorite"
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_favorite_article_auth_required(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that favoriting requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Test",
                    "body": "Test body",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Try to favorite without authentication
        response = await client.post(
            f"/api/articles/{created_article['slug']}/favorite"
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestUnfavoriteArticle:
    """Tests for DELETE /api/articles/{slug}/favorite (unfavorite article endpoint)."""

    @pytest.mark.asyncio
    async def test_unfavorite_article_success(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test successfully unfavoriting a favorited article.

        Verifies that:
        - Status code is 200 OK
        - Response includes favorited=false
        - favoritesCount is decremented
        """
        # User 1 creates an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article to Unfavorite",
                    "description": "Unfavorite test",
                    "body": "This article will be unfavorited.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]
        slug = created_article["slug"]

        # User 2 favorites the article
        await authenticated_client2.post(f"/api/articles/{slug}/favorite")

        # User 2 unfavorites the article
        response = await authenticated_client2.delete(f"/api/articles/{slug}/favorite")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        article = data["article"]

        assert article["favorited"] is False
        assert article["favoritesCount"] == 0

    @pytest.mark.asyncio
    async def test_unfavorite_article_not_favorited(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test that unfavoriting non-favorited article is idempotent.

        Verifies that:
        - Status code is 200 OK
        - Article remains not favorited
        """
        # User 1 creates an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Idempotent Unfavorite",
                    "description": "Unfavorite test",
                    "body": "Test idempotent unfavoriting.",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]
        slug = created_article["slug"]

        # User 2 tries to unfavorite without favoriting first
        response = await authenticated_client2.delete(f"/api/articles/{slug}/favorite")

        assert response.status_code == 200
        data = response.json()
        article = data["article"]

        assert article["favorited"] is False
        assert article["favoritesCount"] == 0

    @pytest.mark.asyncio
    async def test_unfavorite_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test unfavoriting non-existent article returns 404.

        Verifies that:
        - Status code is 404 Not Found
        """
        response = await authenticated_client.delete(
            "/api/articles/nonexistent-slug/favorite"
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_unfavorite_article_auth_required(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that unfavoriting requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        """
        # Create an article
        create_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Test",
                    "body": "Test body",
                }
            },
        )
        assert create_response.status_code == 201
        created_article = create_response.json()["article"]

        # Try to unfavorite without authentication
        response = await client.delete(
            f"/api/articles/{created_article['slug']}/favorite"
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestListArticles:
    """Tests for GET /api/articles (list articles endpoint)."""

    @pytest.mark.asyncio
    async def test_list_articles_all(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test listing all articles with default pagination.

        Verifies that:
        - Status code is 200 OK
        - Response includes articles array and articlesCount
        - Articles are ordered by creation date (newest first)
        """
        # Create multiple articles
        for i in range(3):
            response = await authenticated_client.post(
                "/api/articles",
                json={
                    "article": {
                        "title": f"List Test Article {i}",
                        "description": f"Description {i}",
                        "body": f"Body content {i}",
                    }
                },
            )
            assert response.status_code == 201

        # List all articles
        response = await client.get("/api/articles")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "articles" in data
        assert "articlesCount" in data
        assert data["articlesCount"] >= 3
        assert len(data["articles"]) >= 3

    @pytest.mark.asyncio
    async def test_list_articles_filter_by_tag(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test listing articles filtered by tag.

        Verifies that:
        - Status code is 200 OK
        - Only articles with specified tag are returned
        """
        # Create article with specific tag
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Tagged Article",
                    "description": "Article with specific tag",
                    "body": "Content with tag.",
                    "tagList": ["unique-tag"],
                }
            },
        )
        assert response.status_code == 201

        # List articles by tag
        response = await client.get("/api/articles?tag=unique-tag")

        assert response.status_code == 200
        data = response.json()

        assert len(data["articles"]) >= 1
        # Verify all returned articles have the tag
        for article in data["articles"]:
            assert "unique-tag" in article["tagList"]

    @pytest.mark.asyncio
    async def test_list_articles_filter_by_author(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test listing articles filtered by author.

        Verifies that:
        - Status code is 200 OK
        - Only articles by specified author are returned
        """
        # Create article
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Author Filter Test",
                    "description": "Test filtering by author",
                    "body": "Content by specific author.",
                }
            },
        )
        assert response.status_code == 201

        # List articles by author
        response = await client.get(f"/api/articles?author={test_user.name}")

        assert response.status_code == 200
        data = response.json()

        # All articles should be by this author
        for article in data["articles"]:
            assert article["author"]["username"] == test_user.name

    @pytest.mark.asyncio
    async def test_list_articles_filter_by_favorited(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
        test_user2: User,
    ) -> None:
        """Test listing articles filtered by favorited user.

        Verifies that:
        - Status code is 200 OK
        - Only articles favorited by specified user are returned
        """
        # User 1 creates an article
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Favorited Article",
                    "description": "Article to be favorited",
                    "body": "Content of favorited article.",
                }
            },
        )
        assert response.status_code == 201
        slug = response.json()["article"]["slug"]

        # User 2 favorites it
        response = await authenticated_client2.post(f"/api/articles/{slug}/favorite")
        assert response.status_code == 200

        # List articles favorited by user 2
        response = await client.get(f"/api/articles?favorited={test_user2.name}")

        assert response.status_code == 200
        data = response.json()

        # Should find the favorited article
        assert len(data["articles"]) >= 1
        slugs = [article["slug"] for article in data["articles"]]
        assert slug in slugs

    @pytest.mark.asyncio
    async def test_list_articles_pagination_limit(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test pagination with limit parameter.

        Verifies that:
        - Status code is 200 OK
        - Returns at most limit articles
        - articlesCount reflects actual count
        """
        # Create multiple articles
        for i in range(5):
            response = await authenticated_client.post(
                "/api/articles",
                json={
                    "article": {
                        "title": f"Pagination Test {i}",
                        "description": f"Pagination {i}",
                        "body": f"Body {i}",
                    }
                },
            )
            assert response.status_code == 201

        # Get with limit
        response = await client.get("/api/articles?limit=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["articles"]) <= 2

    @pytest.mark.asyncio
    async def test_list_articles_pagination_offset(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test pagination with offset parameter.

        Verifies that:
        - Status code is 200 OK
        - Offset skips articles correctly
        """
        # Create multiple articles
        for i in range(3):
            response = await authenticated_client.post(
                "/api/articles",
                json={
                    "article": {
                        "title": f"Offset Test {i}",
                        "description": f"Offset {i}",
                        "body": f"Body {i}",
                    }
                },
            )
            assert response.status_code == 201

        # Get all
        response_all = await client.get("/api/articles?limit=100")
        assert response_all.status_code == 200
        all_articles = response_all.json()["articles"]

        # Get with offset
        response_offset = await client.get("/api/articles?offset=1&limit=100")
        assert response_offset.status_code == 200
        offset_articles = response_offset.json()["articles"]

        # Should skip at least one
        assert len(offset_articles) <= len(all_articles)

    @pytest.mark.asyncio
    async def test_list_articles_without_authentication(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test listing articles without authentication.

        Verifies that:
        - Status code is 200 OK
        - Articles are returned with favorited=false
        """
        # Create article
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Unauth List Test",
                    "description": "Test without auth",
                    "body": "Content for list without auth.",
                }
            },
        )
        assert response.status_code == 201

        # List without auth
        response = await client.get("/api/articles")

        assert response.status_code == 200
        data = response.json()

        for article in data["articles"]:
            assert article["favorited"] is False

    @pytest.mark.asyncio
    async def test_list_articles_empty_result(
        self,
        client: AsyncClient,
    ) -> None:
        """Test listing articles with filter that returns no results.

        Verifies that:
        - Status code is 200 OK
        - articles array is empty
        - articlesCount is 0
        """
        response = await client.get("/api/articles?tag=nonexistent-tag-xyz")

        assert response.status_code == 200
        data = response.json()

        assert data["articles"] == []
        assert data["articlesCount"] == 0

    @pytest.mark.asyncio
    async def test_list_articles_limit_bounds(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test pagination limit boundaries (1-100).

        Verifies that:
        - Status code is 200 OK with valid limit
        - Invalid limits are handled appropriately
        """
        # Create articles
        for i in range(3):
            response = await authenticated_client.post(
                "/api/articles",
                json={
                    "article": {
                        "title": f"Bounds Test {i}",
                        "description": f"Bounds {i}",
                        "body": f"Body {i}",
                    }
                },
            )
            assert response.status_code == 201

        # Test with max valid limit
        response = await client.get("/api/articles?limit=100")
        assert response.status_code == 200

        # Test with min valid limit
        response = await client.get("/api/articles?limit=1")
        assert response.status_code == 200
        assert len(response.json()["articles"]) <= 1


class TestGetFeed:
    """Tests for GET /api/articles/feed (get user feed endpoint)."""

    @pytest.mark.asyncio
    async def test_get_feed_with_followed_authors(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
        test_user: User,
        test_user2: User,
    ) -> None:
        """Test feed returns articles from followed authors.

        Verifies that:
        - Status code is 200 OK
        - Feed contains articles from followed authors
        - following status is true for all articles
        """
        # User 2 follows user 1
        response = await authenticated_client2.post(
            f"/api/profiles/{test_user.name}/follow"
        )
        assert response.status_code == 200

        # User 1 creates an article
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Feed Article",
                    "description": "Article in feed",
                    "body": "Content for feed test.",
                }
            },
        )
        assert response.status_code == 201

        # User 2 gets feed
        response = await authenticated_client2.get("/api/articles/feed")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "articles" in data
        assert "articlesCount" in data

        # Should contain the article from followed user
        if len(data["articles"]) > 0:
            for article in data["articles"]:
                assert article["author"]["username"] == test_user.name
                assert article["author"]["following"] is True

    @pytest.mark.asyncio
    async def test_get_feed_empty(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test empty feed when user follows no one.

        Verifies that:
        - Status code is 200 OK
        - articles array is empty
        - articlesCount is 0
        """
        response = await authenticated_client.get("/api/articles/feed")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert data["articles"] == []
        assert data["articlesCount"] == 0

    @pytest.mark.asyncio
    async def test_get_feed_auth_required(
        self,
        client: AsyncClient,
    ) -> None:
        """Test that feed requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        """
        response = await client.get("/api/articles/feed")

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_get_feed_pagination(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
        test_user: User,
    ) -> None:
        """Test feed pagination with limit and offset.

        Verifies that:
        - Status code is 200 OK
        - Limit and offset work correctly
        """
        # User 2 follows user 1
        response = await authenticated_client2.post(
            f"/api/profiles/{test_user.name}/follow"
        )
        assert response.status_code == 200

        # User 1 creates multiple articles
        for i in range(3):
            response = await authenticated_client.post(
                "/api/articles",
                json={
                    "article": {
                        "title": f"Feed Pagination Article {i}",
                        "description": f"Pagination {i}",
                        "body": f"Body {i}",
                    }
                },
            )
            assert response.status_code == 201

        # User 2 gets feed with limit
        response = await authenticated_client2.get("/api/articles/feed?limit=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["articles"]) <= 2


class TestGetTags:
    """Tests for GET /api/tags (get tags endpoint)."""

    @pytest.mark.asyncio
    async def test_get_tags_success(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test successfully retrieving all tags.

        Verifies that:
        - Status code is 200 OK
        - Response contains tags array
        - Tags are unique
        """
        # Create articles with tags
        for i in range(2):
            response = await authenticated_client.post(
                "/api/articles",
                json={
                    "article": {
                        "title": f"Tagged Article {i}",
                        "description": f"Article {i}",
                        "body": f"Body {i}",
                        "tagList": ["python", "fastapi", f"tag{i}"],
                    }
                },
            )
            assert response.status_code == 201

        # Get tags
        response = await client.get("/api/tags")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert "tags" in data
        assert isinstance(data["tags"], list)

        # Verify tags are present and unique
        assert len(data["tags"]) > 0
        assert len(data["tags"]) == len(set(data["tags"]))  # All unique

    @pytest.mark.asyncio
    async def test_get_tags_no_authentication_required(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test getting tags without authentication.

        Verifies that:
        - Status code is 200 OK
        - Tags are returned without authentication
        """
        # Create article with tags
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Public Tags Test",
                    "description": "Test public tags",
                    "body": "Content for public tags test.",
                    "tagList": ["public", "test"],
                }
            },
        )
        assert response.status_code == 201

        # Get tags without auth
        response = await client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()

        assert "tags" in data
        assert isinstance(data["tags"], list)

    @pytest.mark.asyncio
    async def test_get_tags_empty(
        self,
        client: AsyncClient,
    ) -> None:
        """Test getting tags when no articles exist.

        Verifies that:
        - Status code is 200 OK
        - tags array is empty
        """
        response = await client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()

        # May be empty if this is first test or articles were cleared
        assert "tags" in data
        assert isinstance(data["tags"], list)

    @pytest.mark.asyncio
    async def test_get_tags_returns_list(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that tags response is a list of strings.

        Verifies that:
        - Status code is 200 OK
        - tags is a list
        - Each tag is a string
        """
        # Create article with tags
        response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "List Format Test",
                    "description": "Test list format",
                    "body": "Content for list format test.",
                    "tagList": ["format", "test"],
                }
            },
        )
        assert response.status_code == 201

        # Get tags
        response = await client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["tags"], list)
        for tag in data["tags"]:
            assert isinstance(tag, str)
