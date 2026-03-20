"""Tests for comments use cases."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.core.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
)
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email, Password
from src.modules.comments.application.commands.create_comment import CreateComment
from src.modules.comments.application.commands.delete_comment import DeleteComment
from src.modules.comments.application.dtos import CreateCommentRequest
from src.modules.comments.application.queries.list_comments import ListComments
from src.modules.comments.domain.entities import Comment
from src.modules.comments.domain.repositories import ICommentRepository


class TestCreateComment:
    """Tests for CreateComment use case."""

    @pytest.fixture
    def mock_comment_repo(self) -> AsyncMock:
        """Create a mock comment repository."""
        return AsyncMock(spec=ICommentRepository)

    @pytest.fixture
    def mock_user_repo(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def use_case(
        self, mock_comment_repo: AsyncMock, mock_user_repo: AsyncMock
    ) -> CreateComment:
        """Create CreateComment use case."""
        return CreateComment(mock_comment_repo, mock_user_repo)

    @pytest.mark.asyncio
    async def test_create_comment_success(
        self,
        use_case: CreateComment,
        mock_comment_repo: AsyncMock,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test successfully creating a comment."""
        # Arrange
        request = CreateCommentRequest(
            body="Great article!",
            author_id=1,
            article_id=1,
        )

        created_comment = Comment(
            id=1,
            body="Great article!",
            author_id=1,
            article_id=1,
        )
        mock_comment_repo.add.return_value = created_comment

        author = User(
            id=1,
            email=Email("author@example.com"),
            name="Author",
            password=Password.from_raw("password123"),
        )
        mock_user_repo.get.return_value = author

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.body == "Great article!"
        assert result.author.name == "Author"
        mock_comment_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_comment_author_not_found(
        self,
        use_case: CreateComment,
        mock_comment_repo: AsyncMock,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test creating comment when author not found."""
        # Arrange
        request = CreateCommentRequest(
            body="Great article!",
            author_id=1,
            article_id=1,
        )

        created_comment = Comment(
            id=1,
            body="Great article!",
            author_id=1,
            article_id=1,
        )
        mock_comment_repo.add.return_value = created_comment
        mock_user_repo.get.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request)


class TestDeleteComment:
    """Tests for DeleteComment use case."""

    @pytest.fixture
    def mock_comment_repo(self) -> AsyncMock:
        """Create a mock comment repository."""
        return AsyncMock(spec=ICommentRepository)

    @pytest.fixture
    def use_case(self, mock_comment_repo: AsyncMock) -> DeleteComment:
        """Create DeleteComment use case."""
        return DeleteComment(mock_comment_repo)

    @pytest.mark.asyncio
    async def test_delete_comment_success(
        self,
        use_case: DeleteComment,
        mock_comment_repo: AsyncMock,
    ) -> None:
        """Test successfully deleting a comment."""
        # Arrange
        comment = Comment(
            id=1,
            body="Test comment",
            author_id=1,
            article_id=1,
        )
        mock_comment_repo.get.return_value = comment

        # Act
        await use_case.execute(1, 1)

        # Assert
        mock_comment_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(
        self,
        use_case: DeleteComment,
        mock_comment_repo: AsyncMock,
    ) -> None:
        """Test deleting non-existent comment."""
        # Arrange
        mock_comment_repo.get.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(1, 1)

    @pytest.mark.asyncio
    async def test_delete_comment_not_author(
        self,
        use_case: DeleteComment,
        mock_comment_repo: AsyncMock,
    ) -> None:
        """Test deleting comment by non-author."""
        # Arrange
        comment = Comment(
            id=1,
            body="Test comment",
            author_id=1,  # Author is user 1
            article_id=1,
        )
        mock_comment_repo.get.return_value = comment

        # Act & Assert
        with pytest.raises(AuthorizationException):
            await use_case.execute(1, 2)  # User 2 trying to delete


class TestListComments:
    """Tests for ListComments use case."""

    @pytest.fixture
    def mock_comment_repo(self) -> AsyncMock:
        """Create a mock comment repository."""
        return AsyncMock(spec=ICommentRepository)

    @pytest.fixture
    def mock_user_repo(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def use_case(
        self, mock_comment_repo: AsyncMock, mock_user_repo: AsyncMock
    ) -> ListComments:
        """Create ListComments use case."""
        return ListComments(mock_comment_repo, mock_user_repo)

    @pytest.mark.asyncio
    async def test_list_comments_success(
        self,
        use_case: ListComments,
        mock_comment_repo: AsyncMock,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test successfully listing comments."""
        # Arrange
        comments = [
            Comment(id=1, body="Comment 1", author_id=1, article_id=1),
            Comment(id=2, body="Comment 2", author_id=2, article_id=1),
        ]
        mock_comment_repo.list_by_article.return_value = comments

        author1 = User(
            id=1,
            email=Email("author1@example.com"),
            name="Author1",
            password=Password.from_raw("password123"),
        )
        author2 = User(
            id=2,
            email=Email("author2@example.com"),
            name="Author2",
            password=Password.from_raw("password123"),
        )
        mock_user_repo.get.side_effect = [author1, author2]

        # Act
        result = await use_case.execute(1, None)

        # Assert
        assert len(result) == 2
        assert result[0].body == "Comment 1"
        assert result[0].author.name == "Author1"
        assert result[1].body == "Comment 2"
        assert result[1].author.name == "Author2"

    @pytest.mark.asyncio
    async def test_list_comments_empty(
        self,
        use_case: ListComments,
        mock_comment_repo: AsyncMock,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test listing comments when none exist."""
        # Arrange
        mock_comment_repo.list_by_article.return_value = []

        # Act
        result = await use_case.execute(1, None)

        # Assert
        assert len(result) == 0
