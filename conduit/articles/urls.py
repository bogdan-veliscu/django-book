from django.urls import path
from rest_framework.routers import DefaultRouter

from conduit.articles import views
from config import settings
from django.conf.urls.static import static
from django.urls import include

router = DefaultRouter(trailing_slash=False)
router.register(r'articles', views.ArticleViewSet)
router.register(r'tags', views.TagView, basename='tags')

urlpatterns = router.urls

urlpatterns += [
    path('articles/<int:article_id>/favorite', views.favorite, name='article_favorite'),
]

urlpatterns += [
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
    path("search/", views.search_articles, name="article-search"),
    path("ranking/", views.ranked_articles, name="ranking"),
    path("latest_comments/", views.latest_comments, name="latest_comments"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
