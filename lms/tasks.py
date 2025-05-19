from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from mail_templated import send_mail

from lms.models import Course
from users.models import User

User = get_user_model()


@shared_task
def send_course_update_email(course_id, user_id):
    """Отправляет email об обновлении курса."""
    user = User.objects.get(pk=user_id)
    course = Course.objects.get(pk=course_id)

    course_url = settings.SITE_URL + reverse("course-detail", kwargs={"pk": course_id})

    # Отправка email
    send_mail(
        template_name="lms/course_update_email.html",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        context={"user": user, "course": course, "course_url": course_url},
        fail_silently=False,
    )


@shared_task
def block_inactive_users():
    """Блокирует пользователей, которые не заходили более месяца."""
    month_ago = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)  # type: ignore
    for user in inactive_users:
        user.is_active = False
        user.save()
        print(f"Пользователь {user.email} заблокирован.")
