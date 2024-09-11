import shutil
import tempfile
from unittest import mock

import pytest
from django.conf import settings
from django.test import TestCase, override_settings

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
