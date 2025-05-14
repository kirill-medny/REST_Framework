from rest_framework import serializers

from lms.models import Course, Lesson

from .validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"

    def validate_video_link(self, value):
        """
        Проверьте правильность поля video_link.
        """
        validate_youtube_link(value)  # Используем наш валидатор
        return value


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context[
            "request"
        ].user  # Получить текущего пользователя из контекста запроса
        if user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
