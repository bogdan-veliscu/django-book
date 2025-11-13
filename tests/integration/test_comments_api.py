"""Integration tests for Comments API endpoints.

This module contains comprehensive integration tests for the comments
endpoints including creation, listing, and deletion.

Test scenarios include:
- Creating comments on existing articles
- Listing comments with/without authentication
- Deleting comments with authorization checks
- Handling article not found scenarios
- Validating comment body requirements
"""

import pytest
from httpx import AsyncClient

from src.modules.auth.domain.entities import User


class TestCreateComment:
    """Tests for POST /api/articles/{slug}/comments (create comment endpoint)."""

    @pytest.mark.asyncio
    async def test_create_comment_success(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful comment creation on an existing article.

        Verifies that:
        - Status code is 201 Created
        - Response contains comment data with all fields
        - Author is set to current user
        - Response includes correct structure (wrapped in "comment" key)
        - Comment body is preserved
        """
        # First, create an article to comment on
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article for Comments",
                    "description": "Article to test comment creation",
                    "body": "This article will be commented on",
                    "tagList": ["test", "comments"],
                }
            },
        )
        assert article_response.status_code == 201
        article_slug = article_response.json()["article"]["slug"]

        # Now create a comment on the article
        response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "This is a test comment on the article",
                }
            },
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "comment" in data
        comment = data["comment"]

        # Verify comment fields
        assert comment["body"] == "This is a test comment on the article"
        assert "id" in comment
        assert comment["id"] is not None

        # Verify author information
        assert comment["author"]["username"] == test_user.name
        assert "bio" in comment["author"]
        assert "image" in comment["author"]
        assert "following" in comment["author"]

        # Verify timestamps exist
        assert "createdAt" in comment
        assert "updatedAt" in comment

    @pytest.mark.asyncio
    async def test_create_comment_auth_required(
        self,
        client: AsyncClient,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that creating comment requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing authorization
        """
        # First create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Try to create comment without authentication
        response = await client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Unauthorized comment",
                }
            },
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_comment_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating comment fails when article doesn't exist.

        Verifies that:
        - Status code is 404 Not Found
        - Error indicates article not found
        """
        response = await authenticated_client.post(
            "/api/articles/non-existent-article/comments",
            json={
                "comment": {
                    "body": "Comment on non-existent article",
                }
            },
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_comment_empty_body(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating comment fails with empty body.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation failure for empty body
        """
        # First create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Try to create comment with empty body
        response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_comment_whitespace_only_body(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating comment fails with whitespace-only body.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates validation failure for empty/whitespace body
        """
        # First create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Try to create comment with whitespace-only body
        response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "   \n\t  ",
                }
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_comment_missing_body(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating comment fails when body is missing.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Error indicates missing required field
        """
        # First create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Try to create comment without body
        response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {},
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_comment_invalid_request_body(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test creating comment fails with malformed request body.

        Verifies that:
        - Status code is 422 Unprocessable Entity
        - Request missing the required "comment" wrapper key fails
        """
        # First create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Try to create comment with incorrect wrapper
        response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "body": "Comment without wrapper",
            },
        )

        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_create_multiple_comments_on_same_article(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test creating multiple comments on the same article.

        Verifies that:
        - Multiple comments can be created on same article
        - Each comment has unique ID
        - All comments are returned with correct data
        """
        # Create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create first comment
        response1 = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "First comment on this article",
                }
            },
        )
        assert response1.status_code == 201
        comment1_id = response1.json()["comment"]["id"]

        # Create second comment
        response2 = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Second comment on this article",
                }
            },
        )
        assert response2.status_code == 201
        comment2_id = response2.json()["comment"]["id"]

        # Verify comments have different IDs
        assert comment1_id != comment2_id

        # Verify first comment
        assert response1.json()["comment"]["body"] == "First comment on this article"
        assert response1.json()["comment"]["author"]["username"] == test_user.name

        # Verify second comment
        assert response2.json()["comment"]["body"] == "Second comment on this article"
        assert response2.json()["comment"]["author"]["username"] == test_user.name


class TestListComments:
    """Tests for GET /api/articles/{slug}/comments (list comments endpoint)."""

    @pytest.mark.asyncio
    async def test_list_comments_success(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successfully listing comments on an existing article.

        Verifies that:
        - Status code is 200 OK
        - Response contains list of comments
        - Each comment has correct structure
        - Response has correct structure (wrapped in "comments" key)
        """
        # Create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create some comments
        for i in range(3):
            await authenticated_client.post(
                f"/api/articles/{article_slug}/comments",
                json={
                    "comment": {
                        "body": f"Test comment {i + 1}",
                    }
                },
            )

        # List comments
        response = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response structure
        assert "comments" in data
        comments = data["comments"]

        # Verify we got all comments
        assert len(comments) == 3

        # Verify each comment has correct structure
        for idx, comment in enumerate(comments):
            assert "id" in comment
            assert comment["body"] == f"Test comment {idx + 1}"
            assert "author" in comment
            assert comment["author"]["username"] == test_user.name
            assert "following" in comment["author"]
            assert "createdAt" in comment
            assert "updatedAt" in comment

    @pytest.mark.asyncio
    async def test_list_comments_empty_article(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test listing comments on article with no comments.

        Verifies that:
        - Status code is 200 OK
        - Comments list is empty
        - Response has correct structure
        """
        # Create an article without comments
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article Without Comments",
                    "description": "No comments here",
                    "body": "Empty article",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # List comments
        response = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify response is empty list
        assert "comments" in data
        assert len(data["comments"]) == 0

    @pytest.mark.asyncio
    async def test_list_comments_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test listing comments fails when article doesn't exist.

        Verifies that:
        - Status code is 404 Not Found
        - Error indicates article not found
        """
        response = await authenticated_client.get(
            "/api/articles/non-existent-article/comments",
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_list_comments_without_authentication(
        self,
        authenticated_client: AsyncClient,
        client: AsyncClient,
    ) -> None:
        """Test listing comments works without authentication.

        Verifies that:
        - Status code is 200 OK
        - Comments can be retrieved without authentication
        - Author information is included
        """
        # Create an article with comments
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create a comment
        await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Test comment",
                }
            },
        )

        # List comments without authentication
        response = await client.get(
            f"/api/articles/{article_slug}/comments",
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        # Verify comments are returned
        assert "comments" in data
        assert len(data["comments"]) == 1
        assert data["comments"][0]["body"] == "Test comment"

    @pytest.mark.asyncio
    async def test_list_comments_with_authentication(
        self,
        authenticated_client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test listing comments with authentication includes following status.

        Verifies that:
        - Status code is 200 OK
        - Following status is included for comment authors
        - For own comments, following should be false
        """
        # Create an article with comments
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create a comment
        await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Test comment",
                }
            },
        )

        # List comments with authentication
        response = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )

        assert response.status_code == 200
        data = response.json()

        # Verify following status is included
        assert len(data["comments"]) == 1
        comment = data["comments"][0]
        assert "following" in comment["author"]

    @pytest.mark.asyncio
    async def test_list_comments_ordered_by_creation_time(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that comments are ordered by creation time.

        Verifies that:
        - Comments are returned in creation order
        - Earlier comments appear first
        """
        # Create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create comments in order
        comment_bodies = []
        for i in range(3):
            body = f"Comment {i + 1}"
            comment_bodies.append(body)
            await authenticated_client.post(
                f"/api/articles/{article_slug}/comments",
                json={
                    "comment": {
                        "body": body,
                    }
                },
            )

        # List comments
        response = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )

        assert response.status_code == 200
        data = response.json()
        comments = data["comments"]

        # Verify order (should be in creation order: first created first)
        assert len(comments) == 3
        for i, comment in enumerate(comments):
            assert comment["body"] == comment_bodies[i]

    @pytest.mark.asyncio
    async def test_list_comments_multiple_articles(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test listing comments returns only comments for the article.

        Verifies that:
        - Comments from other articles are not included
        - Only comments for specified article are returned
        """
        # Create first article with comments
        article1_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article 1",
                    "description": "First article",
                    "body": "Body 1",
                }
            },
        )
        article1_slug = article1_response.json()["article"]["slug"]

        # Create second article with comments
        article2_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Article 2",
                    "description": "Second article",
                    "body": "Body 2",
                }
            },
        )
        article2_slug = article2_response.json()["article"]["slug"]

        # Add comments to first article
        await authenticated_client.post(
            f"/api/articles/{article1_slug}/comments",
            json={
                "comment": {
                    "body": "Comment on article 1",
                }
            },
        )

        # Add comments to second article
        for i in range(2):
            await authenticated_client.post(
                f"/api/articles/{article2_slug}/comments",
                json={
                    "comment": {
                        "body": f"Comment {i + 1} on article 2",
                    }
                },
            )

        # List comments for first article
        response1 = await authenticated_client.get(
            f"/api/articles/{article1_slug}/comments",
        )

        # List comments for second article
        response2 = await authenticated_client.get(
            f"/api/articles/{article2_slug}/comments",
        )

        # Verify correct comments are returned
        assert len(response1.json()["comments"]) == 1
        assert response1.json()["comments"][0]["body"] == "Comment on article 1"

        assert len(response2.json()["comments"]) == 2
        assert response2.json()["comments"][0]["body"] == "Comment 1 on article 2"
        assert response2.json()["comments"][1]["body"] == "Comment 2 on article 2"


class TestDeleteComment:
    """Tests for DELETE /api/articles/{slug}/comments/{comment_id} (delete comment endpoint)."""

    @pytest.mark.asyncio
    async def test_delete_comment_success(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test successfully deleting a comment by the author.

        Verifies that:
        - Status code is 204 No Content
        - Comment is removed from article
        - No response body is returned
        """
        # Create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create a comment
        comment_response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Comment to delete",
                }
            },
        )
        comment_id = comment_response.json()["comment"]["id"]

        # Delete the comment
        delete_response = await authenticated_client.delete(
            f"/api/articles/{article_slug}/comments/{comment_id}",
        )

        assert (
            delete_response.status_code == 204
        ), f"Expected 204, got {delete_response.status_code}"

        # Verify comment is deleted by listing comments
        list_response = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )
        assert len(list_response.json()["comments"]) == 0

    @pytest.mark.asyncio
    async def test_delete_comment_auth_required(
        self,
        authenticated_client: AsyncClient,
        client: AsyncClient,
    ) -> None:
        """Test that deleting comment requires authentication.

        Verifies that:
        - Status code is 401 Unauthorized
        - Error indicates missing authorization
        """
        # Create an article and comment
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        comment_response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Comment to delete",
                }
            },
        )
        comment_id = comment_response.json()["comment"]["id"]

        # Try to delete without authentication
        response = await client.delete(
            f"/api/articles/{article_slug}/comments/{comment_id}",
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_comment_not_author(
        self,
        authenticated_client: AsyncClient,
        authenticated_client2: AsyncClient,
    ) -> None:
        """Test that non-author cannot delete comment.

        Verifies that:
        - Status code is 403 Forbidden
        - Error indicates not authorized to delete
        """
        # Create an article and comment as user 1
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        comment_response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Comment by user 1",
                }
            },
        )
        comment_id = comment_response.json()["comment"]["id"]

        # Try to delete as user 2
        response = await authenticated_client2.delete(
            f"/api/articles/{article_slug}/comments/{comment_id}",
        )

        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

        # Verify comment still exists
        list_response = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )
        assert len(list_response.json()["comments"]) == 1

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test deleting non-existent comment fails.

        Verifies that:
        - Status code is 404 Not Found
        - Error indicates comment not found
        """
        # Create an article
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Try to delete non-existent comment
        response = await authenticated_client.delete(
            f"/api/articles/{article_slug}/comments/99999",
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_comment_article_not_found(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test deleting comment fails when article doesn't exist.

        Verifies that:
        - Status code is 404 Not Found
        - Error indicates article not found
        """
        response = await authenticated_client.delete(
            "/api/articles/non-existent-article/comments/123",
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_delete_comment_idempotent(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that deleting the same comment twice fails on second attempt.

        Verifies that:
        - First delete returns 204
        - Second delete returns 404 (comment already deleted)
        """
        # Create an article and comment
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        comment_response = await authenticated_client.post(
            f"/api/articles/{article_slug}/comments",
            json={
                "comment": {
                    "body": "Comment to delete",
                }
            },
        )
        comment_id = comment_response.json()["comment"]["id"]

        # First delete succeeds
        delete_response1 = await authenticated_client.delete(
            f"/api/articles/{article_slug}/comments/{comment_id}",
        )
        assert delete_response1.status_code == 204

        # Second delete fails with 404
        delete_response2 = await authenticated_client.delete(
            f"/api/articles/{article_slug}/comments/{comment_id}",
        )
        assert delete_response2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_comment_removes_from_list(
        self,
        authenticated_client: AsyncClient,
    ) -> None:
        """Test that deleted comment is no longer in comment list.

        Verifies that:
        - Comment count decrements after deletion
        - Deleted comment is not in response
        """
        # Create an article with multiple comments
        article_response = await authenticated_client.post(
            "/api/articles",
            json={
                "article": {
                    "title": "Test Article",
                    "description": "Description",
                    "body": "Body content",
                }
            },
        )
        article_slug = article_response.json()["article"]["slug"]

        # Create comments
        comment_ids = []
        for i in range(3):
            comment_response = await authenticated_client.post(
                f"/api/articles/{article_slug}/comments",
                json={
                    "comment": {
                        "body": f"Comment {i + 1}",
                    }
                },
            )
            comment_ids.append(comment_response.json()["comment"]["id"])

        # Verify 3 comments exist
        list_response1 = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )
        assert len(list_response1.json()["comments"]) == 3

        # Delete the second comment
        delete_response = await authenticated_client.delete(
            f"/api/articles/{article_slug}/comments/{comment_ids[1]}",
        )
        assert delete_response.status_code == 204

        # Verify 2 comments remain
        list_response2 = await authenticated_client.get(
            f"/api/articles/{article_slug}/comments",
        )
        remaining_comments = list_response2.json()["comments"]
        assert len(remaining_comments) == 2

        # Verify correct comments remain
        remaining_bodies = [c["body"] for c in remaining_comments]
        assert "Comment 1" in remaining_bodies
        assert "Comment 2" not in remaining_bodies
        assert "Comment 3" in remaining_bodies
