from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles import views

router = DefaultRouter(trailing_slash=False)
router.register("articles", views.ArticleViewSet)
router.register("tags", views.TagView)

urlpatterns = [
    path("api/", include(router.urls)),
    path("articles", views.ArticleListView.as_view(), name="article-list"),
    path(
        "articles/<slug:slug>",
        views.ArticleDetailView.as_view(),
        name="article-detail-view",
    ),
    path("articles/new", views.ArticleCreateView.as_view(), name="create-article"),
]
