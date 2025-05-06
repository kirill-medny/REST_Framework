from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_youtube_link(value):
    """
    Валидатор для проверки того, является ли ссылка действительной на YouTube.
    """
    parsed_url = urlparse(value)
    if parsed_url.netloc != "www.youtube.com" and parsed_url.netloc != "youtube.com":
        raise ValidationError("Only YouTube links are allowed.")
