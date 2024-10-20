import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from articles.models import Article
from tests.factories import ArticleFactory, UserFactory


@pytest.mark.django_db
def test_article_list_template(client, articles):
    response = client.get(reverse("article-list"))
    assertTemplateUsed(
        response, "articles/home.html"
    )  # Ensure the correct template is used
    assert (
        "articles" in response.context
    )  # Verify that the context includes the article list
    assert response.status_code == 200  # Ensure the response is OK