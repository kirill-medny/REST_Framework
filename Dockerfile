FROM python:3.9-slim-buster

# Установите Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./

# Установите зависимости проекта с помощью Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Скопируйте код проекта
COPY . .

# Собираем статику (можно убрать, если не используете статику)
# RUN python manage.py collectstatic --noinput

# Запускаем приложение с помощью Gunicorn
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]