from django.urls import path

from conduit.comments import views

urlpatterns = [
    path('articles/<slug:article_slug>/comments', views.CommentListCreateAPIView.as_view()),
    path('articles/<slug:article_slug>/comments/<int:pk>', views.CommentDestroyAPIView.as_view()),
]
