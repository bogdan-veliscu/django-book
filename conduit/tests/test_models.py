import shutil
import tempfile
from unittest import mock

import pytest
from django.conf import settings
from django.test import TestCase, override_settings

from articles.models import Article
from profiles.models import User
from tests.factories import ArticleFactory


@pytest.mark.django_db
def test_article_creation():
    article = ArticleFactory()
    assert article.title is not None
    assert article.content is not None
    assert article.author is not None
    assert article.tags is not None
    assert article.slug is not None
    assert article.created_at is not None
    assert article.updated_at is not None


@pytest.mark.django_db  # Ensures that the test database is used
def test_create_user():
    user = User.objects.create_user(
        email="john@me.com", name="john", password="pass123"
    )
    assert user.name == "john"
    assert user.is_active  # Check that the user is active by default


@pytest.mark.django_db
def test_check_password():
    user = User.objects.create_user(
        email="john@me.com", name="john", password="pass123"
    )
    assert (
        user.check_password("pass123") is True
    )  # Test that the password is set correctly


@pytest.mark.django_db
def test_create_article():
    Article.objects.create(
        title="Test Article",
        content="Test Content",
        image="test_image.jpg",
        author=User.objects.create_user(
            email="bogdan@brandfocus.ai", name="Bogdan", password="pass123"
        ),
    )
    article = Article.objects.get(title="Test Article")
    assert article.title == "Test Article"
    assert article.content == "Test Content"
    assert article.author.name == "Bogdan"
    assert article.author.email == "bogdan@brandfocus.ai"
    assert article.author.check_password("pass123") is True
