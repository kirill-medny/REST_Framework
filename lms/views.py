from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import permission_classes

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsNotModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["update", "patrial_update"]:
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            permission_classes = [permissions.IsAuthenticated, IsOwner, ~IsModerator]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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
