import os

from celery import Celery
from django.conf import settings

# Установите переменную окружения DJANGO_SETTINGS_MODULE
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "config.settings"
)  # Замените core на название вашего проекта

app = Celery("config")

# Используйте настройки Django для Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
