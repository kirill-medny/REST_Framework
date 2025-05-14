from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer
from users.models import Subscription
from users.permissions import IsModerator, IsOwner

from .paginators import CoursePaginator, LessonPaginator


class SubscriptionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user  # получаем пользователя из self.request
        course_id = request.data.get(
            "course_id"
        )  # получаем id курса из self.request.data

        if not course_id:
            return Response(
                {"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(
            Course, id=course_id
        )  # получаем объект курса из базы с помощью get_object_or_404

        subs_item = Subscription.objects.filter(
            user=user, course=course_item
        )  # получаем объекты подписок по текущему пользователю и курса

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"
        # Возвращаем ответ в API
        return Response({"message": message})


class CourseListAPIView(generics.ListAPIView):  # Используем generics для простоты
    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator
    permission_classes = [permissions.IsAuthenticated]


class CourseDetailAPIView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(tags=["Lessons"], description="List and create Lessons")
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, ~IsModerator]
    pagination_class = LessonPaginator

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(tags=["Lessons"], description="Retrieve, update and destroy Lesson")
class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        elif self.request.method == "DELETE":
            permission_classes = [permissions.IsAuthenticated, IsOwner, ~IsModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


@extend_schema(tags=["Courses"], description="CRUD operations for courses")
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            permission_classes = [permissions.IsAuthenticated, IsOwner, ~IsModerator]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
