from django.urls import path
from rest_framework.routers import DefaultRouter

from conduit.profiles import views

router = DefaultRouter(trailing_slash=False)
router.register(r'profiles', views.ProfileViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('user', views.UserRetrieveUpdateAPIView.as_view()),
    path('users/login', views.UserLoginAPIView.as_view()),
    path('users', views.UserCreateAPIView.as_view()),
]
