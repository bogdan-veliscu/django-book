"""Tests for articles domain."""

import pytest

from src.modules.articles.domain.entities import Article, Tag
from src.modules.articles.domain.value_objects import Slug


class TestSlug:
    """Tests for Slug value object."""

    def test_create_slug_from_text(self) -> None:
        """Test creating a slug from text."""
        slug = Slug.from_text("Hello World!")
        assert slug.value == "hello-world"

    def test_slug_with_special_characters(self) -> None:
        """Test slug generation with special characters."""
        slug = Slug.from_text("This & That: A Story")
        assert slug.value == "this-that-a-story"

    def test_slug_with_numbers(self) -> None:
        """Test slug with numbers."""
        slug = Slug.from_text("Python 3.12 is here!")
        assert slug.value == "python-3-12-is-here"

    def test_slug_equality(self) -> None:
        """Test slug equality."""
        slug1 = Slug("hello-world")
        slug2 = Slug("hello-world")
        slug3 = Slug("goodbye-world")

        assert slug1 == slug2
        assert slug1 != slug3


class TestTag:
    """Tests for Tag entity."""

    def test_create_tag(self) -> None:
        """Test creating a tag."""
        tag = Tag(name="python")
        assert tag.name == "python"

    def test_tag_name_normalization(self) -> None:
        """Test tag name is normalized to lowercase."""
        tag = Tag(name="Python")
        assert tag.name == "python"

    def test_tag_equality(self) -> None:
        """Test tag equality based on name."""
        tag1 = Tag(name="python")
        tag2 = Tag(name="python")
        tag3 = Tag(name="javascript")

        assert tag1 == tag2
        assert tag1 != tag3


class TestArticle:
    """Tests for Article entity."""

    def test_create_article(self) -> None:
        """Test creating an article."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        assert article.title == "Hello World"
        assert article.description == "A simple article"
        assert article.body == "This is the content"
        assert article.author_id == 1
        assert article.slug.value == "hello-world"
        assert article.tags == set()
        assert article.favorites == set()

    def test_article_with_custom_slug(self) -> None:
        """Test creating article with custom slug."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
            slug=Slug("custom-slug"),
        )

        assert article.slug.value == "custom-slug"

    def test_add_tag(self) -> None:
        """Test adding a tag to article."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.add_tag("python")
        assert "python" in article.tags

    def test_remove_tag(self) -> None:
        """Test removing a tag from article."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.add_tag("python")
        article.add_tag("django")
        assert "python" in article.tags

        article.remove_tag("python")
        assert "python" not in article.tags
        assert "django" in article.tags

    def test_has_tag(self) -> None:
        """Test checking if article has a tag."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.add_tag("python")
        assert article.has_tag("python") is True
        assert article.has_tag("javascript") is False

    def test_favorite_by_user(self) -> None:
        """Test favoriting article by user."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.favorite(user_id=2)
        assert 2 in article.favorites
        assert article.is_favorited_by(2) is True

    def test_unfavorite_by_user(self) -> None:
        """Test unfavoriting article by user."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.favorite(user_id=2)
        assert article.is_favorited_by(2) is True

        article.unfavorite(user_id=2)
        assert article.is_favorited_by(2) is False
        assert 2 not in article.favorites

    def test_favorites_count(self) -> None:
        """Test getting favorites count."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.favorite(user_id=2)
        article.favorite(user_id=3)
        article.favorite(user_id=4)

        assert article.favorites_count() == 3

    def test_update_article(self) -> None:
        """Test updating article content."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.update(
            title="Updated Title",
            description="Updated description",
            body="Updated content",
        )

        assert article.title == "Updated Title"
        assert article.description == "Updated description"
        assert article.body == "Updated content"
        # Slug should be updated when title changes
        assert article.slug.value == "updated-title"

    def test_idempotent_favorite(self) -> None:
        """Test that favoriting multiple times is idempotent."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        article.favorite(user_id=2)
        article.favorite(user_id=2)  # Favorite again

        assert len(article.favorites) == 1
        assert 2 in article.favorites

    def test_idempotent_unfavorite(self) -> None:
        """Test that unfavoriting when not favorited is safe."""
        article = Article(
            title="Hello World",
            description="A simple article",
            body="This is the content",
            author_id=1,
        )

        # Unfavorite without favoriting first
        article.unfavorite(user_id=2)
        assert article.is_favorited_by(2) is False
