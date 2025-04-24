from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.urls import app_name

from lms import views

app_name = "lms"

router = DefaultRouter()
router.register(r"courses", views.CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "lessons/", views.LessonListCreateAPIView.as_view(), name="lesson-list-create"
    ),
    path(
        "lessons/<int:pk>/",
        views.LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-retrieve-update-destroy",
    ),
]
