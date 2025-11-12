"""Tests for comments domain entities."""

from datetime import datetime

import pytest

from src.modules.comments.domain.entities import Comment


class TestComment:
    """Tests for Comment entity."""

    def test_create_comment(self) -> None:
        """Test creating a comment."""
        comment = Comment(
            body="This is a great article!",
            author_id=1,
            article_id=1,
        )

        assert comment.body == "This is a great article!"
        assert comment.author_id == 1
        assert comment.article_id == 1
        assert comment.id is None
        assert isinstance(comment.created_at, datetime)
        assert isinstance(comment.updated_at, datetime)

    def test_create_comment_with_id(self) -> None:
        """Test creating a comment with ID."""
        comment = Comment(
            id=1,
            body="This is a great article!",
            author_id=1,
            article_id=1,
        )

        assert comment.id == 1
        assert comment.body == "This is a great article!"

    def test_update_comment_body(self) -> None:
        """Test updating comment body."""
        comment = Comment(
            body="Original body",
            author_id=1,
            article_id=1,
        )

        original_updated_at = comment.updated_at
        comment.update_body("Updated body")

        assert comment.body == "Updated body"
        assert comment.updated_at > original_updated_at

    def test_comment_with_empty_body_raises_error(self) -> None:
        """Test that creating a comment with empty body raises error."""
        from src.core.domain.exceptions import ValidationException

        with pytest.raises(ValidationException, match="Comment body cannot be empty"):
            Comment(body="", author_id=1, article_id=1)

    def test_comment_with_whitespace_body_raises_error(self) -> None:
        """Test that creating a comment with whitespace body raises error."""
        from src.core.domain.exceptions import ValidationException

        with pytest.raises(ValidationException, match="Comment body cannot be empty"):
            Comment(body="   ", author_id=1, article_id=1)

    def test_update_comment_with_empty_body_raises_error(self) -> None:
        """Test that updating comment with empty body raises error."""
        from src.core.domain.exceptions import ValidationException

        comment = Comment(body="Original body", author_id=1, article_id=1)

        with pytest.raises(ValidationException, match="Comment body cannot be empty"):
            comment.update_body("")

    def test_comment_equality(self) -> None:
        """Test comment equality based on ID."""
        comment1 = Comment(id=1, body="Test", author_id=1, article_id=1)
        comment2 = Comment(id=1, body="Different", author_id=2, article_id=2)
        comment3 = Comment(id=2, body="Test", author_id=1, article_id=1)

        assert comment1 == comment2  # Same ID
        assert comment1 != comment3  # Different ID

    def test_comment_without_id_not_equal(self) -> None:
        """Test that comments without ID are not equal."""
        comment1 = Comment(body="Test", author_id=1, article_id=1)
        comment2 = Comment(body="Test", author_id=1, article_id=1)

        assert comment1 != comment2
