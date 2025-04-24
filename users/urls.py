from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users import views

app_name = "users"

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
