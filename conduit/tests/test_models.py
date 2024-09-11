import pytest
from tests.factories import ArticleFactory
import tempfile
import shutil
from django.conf import settings
from django.test import TestCase, override_settings
from unittest import mock

# Create a temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)  # Override MEDIA_ROOT for this test
@mock.patch('os.chmod')  # Mock os.chmod
@mock.patch('os.path.exists', return_value=True) 
class ConduitTest(TestCase):
    
    @classmethod
    def tearDownClass(cls):
        # Clean up after the tests
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()


    @pytest.mark.django_db
    def test_create_article(self, mock_exists, mock_chmod):
        article = ArticleFactory()
        assert article is not None

    @pytest.mark.django_db
    def test_article_fields(self, mock_exists, mock_chmod):
        article = ArticleFactory()
        assert article.title is not None
        assert article.content is not None
        assert article.author is not None
        assert article.tags is not None
        assert article.slug is not None
        assert article.created_at is not None
        assert article.updated_at is not None
