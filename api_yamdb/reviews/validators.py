"""Валидаторы вьсетов приложения reviews."""
from _datetime import datetime
import re

from rest_framework.serializers import ValidationError

from reviews.constants import USERNAME_REGEX_SIGNS


def validate_username(username):
    """Валидатор имени пользователя."""
    if username == 'me':
        raise ValidationError(
            f'Неверное имя пользователя: {username}.'
        )
    check_symbols = re.sub(USERNAME_REGEX_SIGNS, '', username)
    if check_symbols:
        bad_symbols = "".join(set(check_symbols))
        raise ValidationError(
            'Используется запрещенный символ:'
            f'{bad_symbols}'
        )
    return username


def get_current_year():
    """Валидатор года выпуска произведения."""
    return int(datetime.now().year)
