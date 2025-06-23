FROM python:3.10-slim-buster

# Установка системных зависимостей (если нужны)
# RUN apt-get update && apt-get install -y --no-install-recommends <ваши_зависимости>

# Установка Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Копируем pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./

# Установка зависимостей проекта с помощью Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Копируем код проекта
COPY . .

# Собираем статику (если требуется)
RUN poetry run python manage.py collectstatic --noinput

# Запускаем приложение с помощью Gunicorn
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]