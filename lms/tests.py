from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson

User = get_user_model()


class CourseTests(APITestCase):
    def setUp(self):
        # Создаем тест user
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        # Создаем тест course
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.user
        )

    def test_course_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("course-list")  # Используйте имя, которое вы указали в urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 1
        )  # Проверяем, что вернулся один курс
        self.assertEqual(response.data["results"][0]["name"], "Test Course")


class SubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.course = Course.objects.create(
            name="Test Course", description="Test Description", owner=self.user
        )

    def test_subscription_create(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("subscription")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")

    def test_subscription_delete(self):
        # Сначала создайте подписку
        self.client.force_authenticate(user=self.user)
        url = reverse("subscription")
        data = {"course_id": self.course.id}
        self.client.post(url, data)

        # Затем удалите его
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
