from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users import views
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

app_name = "users"

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", views.RegistrationAPIView.as_view(), name="register"),
    path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
