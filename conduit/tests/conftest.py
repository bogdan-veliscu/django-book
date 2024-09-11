import pytest

from tests.factories import ArticleFactory, UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def articles():
    return ArticleFactory.create_batch(5)
