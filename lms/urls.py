from django.urls import path

from lms import views

app_name = "lms"


urlpatterns = [
    path("courses/", views.CourseListAPIView.as_view(), name="course-list"),
    path(
        "courses/<int:pk>/", views.CourseDetailAPIView.as_view(), name="course-detail"
    ),
    path(
        "lessons/", views.LessonListCreateAPIView.as_view(), name="lesson-list-create"
    ),
    path(
        "lessons/<int:pk>/",
        views.LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-retrieve-update-destroy",
    ),
    path("subscriptions/", views.SubscriptionAPIView.as_view(), name="subscription"),
]
