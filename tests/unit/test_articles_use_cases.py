"""Tests for articles use cases."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.core.domain.exceptions import (
    AuthorizationException,
    EntityNotFoundException,
)
from src.modules.articles.application.commands.create_article import CreateArticle
from src.modules.articles.application.commands.delete_article import DeleteArticle
from src.modules.articles.application.commands.favorite_article import FavoriteArticle
from src.modules.articles.application.commands.unfavorite_article import (
    UnfavoriteArticle,
)
from src.modules.articles.application.commands.update_article import UpdateArticle
from src.modules.articles.application.dtos import (
    CreateArticleRequest,
    UpdateArticleRequest,
)
from src.modules.articles.application.queries.get_article import GetArticle
from src.modules.articles.domain.entities import Article
from src.modules.articles.domain.repositories import IArticleRepository
from src.modules.articles.domain.value_objects import Slug
from src.modules.auth.domain.entities import User
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.domain.value_objects import Email, Password


class TestCreateArticle:
    """Tests for CreateArticle use case."""

    @pytest.fixture
    def mock_article_repo(self) -> AsyncMock:
        """Create a mock article repository."""
        return AsyncMock(spec=IArticleRepository)

    @pytest.fixture
    def use_case(self, mock_article_repo: AsyncMock) -> CreateArticle:
        """Create CreateArticle use case."""
        return CreateArticle(mock_article_repo)

    @pytest.mark.asyncio
    async def test_create_article_success(
        self,
        use_case: CreateArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test successfully creating an article."""
        # Arrange
        request = CreateArticleRequest(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            tags=["python", "fastapi"],
            author_id=1,
        )

        created_article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
            slug=Slug.from_text("Hello World"),
            tags={"python", "fastapi"},
        )
        mock_article_repo.add.return_value = created_article

        # Act
        result = await use_case.execute(request)

        # Assert
        assert result.title == "Hello World"
        assert result.slug == "hello-world"
        assert "python" in result.tags
        assert "fastapi" in result.tags
        mock_article_repo.add.assert_called_once()


class TestUpdateArticle:
    """Tests for UpdateArticle use case."""

    @pytest.fixture
    def mock_article_repo(self) -> AsyncMock:
        """Create a mock article repository."""
        return AsyncMock(spec=IArticleRepository)

    @pytest.fixture
    def use_case(self, mock_article_repo: AsyncMock) -> UpdateArticle:
        """Create UpdateArticle use case."""
        return UpdateArticle(mock_article_repo)

    @pytest.mark.asyncio
    async def test_update_article_success(
        self,
        use_case: UpdateArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test successfully updating an article."""
        # Arrange
        article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )
        mock_article_repo.get_by_slug.return_value = article
        mock_article_repo.update.return_value = article

        request = UpdateArticleRequest(
            title="Updated Title",
            description="Updated description",
            body="Updated content",
        )

        # Act
        result = await use_case.execute("hello-world", 1, request)

        # Assert
        assert result.title == "Updated Title"
        mock_article_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_article_not_found(
        self,
        use_case: UpdateArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test updating non-existent article."""
        # Arrange
        mock_article_repo.get_by_slug.return_value = None
        request = UpdateArticleRequest(title="Updated")

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute("nonexistent", 1, request)

    @pytest.mark.asyncio
    async def test_update_article_not_author(
        self,
        use_case: UpdateArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test updating article by non-author."""
        # Arrange
        article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,  # Author is user 1
        )
        mock_article_repo.get_by_slug.return_value = article

        request = UpdateArticleRequest(title="Updated")

        # Act & Assert
        with pytest.raises(AuthorizationException):
            await use_case.execute("hello-world", 2, request)  # User 2 trying to update


class TestDeleteArticle:
    """Tests for DeleteArticle use case."""

    @pytest.fixture
    def mock_article_repo(self) -> AsyncMock:
        """Create a mock article repository."""
        return AsyncMock(spec=IArticleRepository)

    @pytest.fixture
    def use_case(self, mock_article_repo: AsyncMock) -> DeleteArticle:
        """Create DeleteArticle use case."""
        return DeleteArticle(mock_article_repo)

    @pytest.mark.asyncio
    async def test_delete_article_success(
        self,
        use_case: DeleteArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test successfully deleting an article."""
        # Arrange
        article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )
        mock_article_repo.get_by_slug.return_value = article

        # Act
        await use_case.execute("hello-world", 1)

        # Assert
        mock_article_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_article_not_author(
        self,
        use_case: DeleteArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test deleting article by non-author."""
        # Arrange
        article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )
        mock_article_repo.get_by_slug.return_value = article

        # Act & Assert
        with pytest.raises(AuthorizationException):
            await use_case.execute("hello-world", 2)


class TestGetArticle:
    """Tests for GetArticle use case."""

    @pytest.fixture
    def mock_article_repo(self) -> AsyncMock:
        """Create a mock article repository."""
        return AsyncMock(spec=IArticleRepository)

    @pytest.fixture
    def mock_user_repo(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def use_case(
        self, mock_article_repo: AsyncMock, mock_user_repo: AsyncMock
    ) -> GetArticle:
        """Create GetArticle use case."""
        return GetArticle(mock_article_repo, mock_user_repo)

    @pytest.mark.asyncio
    async def test_get_article_success(
        self,
        use_case: GetArticle,
        mock_article_repo: AsyncMock,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test successfully getting an article."""
        # Arrange
        article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
            tags={"python"},
        )
        mock_article_repo.get_by_slug.return_value = article

        author = User(
            id=1,
            email=Email("author@example.com"),
            name="Author",
            password=Password.from_raw("password123"),
        )
        mock_user_repo.get.return_value = author

        # Act
        result = await use_case.execute("hello-world", None)

        # Assert
        assert result.title == "Hello World"
        assert result.slug == "hello-world"
        assert result.author.name == "Author"
        assert "python" in result.tags

    @pytest.mark.asyncio
    async def test_get_article_not_found(
        self,
        use_case: GetArticle,
        mock_article_repo: AsyncMock,
    ) -> None:
        """Test getting non-existent article."""
        # Arrange
        mock_article_repo.get_by_slug.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute("nonexistent", None)


class TestFavoriteArticle:
    """Tests for FavoriteArticle use case."""

    @pytest.fixture
    def mock_article_repo(self) -> AsyncMock:
        """Create a mock article repository."""
        return AsyncMock(spec=IArticleRepository)

    @pytest.fixture
    def mock_user_repo(self) -> AsyncMock:
        """Create a mock user repository."""
        return AsyncMock(spec=IUserRepository)

    @pytest.fixture
    def use_case(
        self, mock_article_repo: AsyncMock, mock_user_repo: AsyncMock
    ) -> FavoriteArticle:
        """Create FavoriteArticle use case."""
        return FavoriteArticle(mock_article_repo, mock_user_repo)

    @pytest.mark.asyncio
    async def test_favorite_article_success(
        self,
        use_case: FavoriteArticle,
        mock_article_repo: AsyncMock,
        mock_user_repo: AsyncMock,
    ) -> None:
        """Test successfully favoriting an article."""
        # Arrange
        article = Article(
            id=1,
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )
        mock_article_repo.get_by_slug.return_value = article
        mock_article_repo.update.return_value = article

        author = User(
            id=1,
            email=Email("author@example.com"),
            name="Author",
            password=Password.from_raw("password123"),
        )
        mock_user_repo.get.return_value = author

        # Act
        result = await use_case.execute("hello-world", 2)

        # Assert
        assert result.favorited is True
        mock_article_repo.update.assert_called_once()
