from articles import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register("articles", views.ArticleViewSet)
router.register("tags", views.TagView)

urlpatterns = [
    path("api/", include(router.urls)),
    path("articles", views.ArticleListView.as_view(), name="article-list"),
    path(
        "articles/new",
        views.ArticleCreateView.as_view(),
        name="create-article-view",
    ),
    path(
        "articles/<slug:slug>",
        views.ArticleDetailView.as_view(),
        name="article-detail-view",
    ),
    # add favorite article path
    path(
        "article/favorite/<int:article_id>/",
        views.favorite,
        name="favorite",
    ),
]
