import re

from rest_framework.serializers import ValidationError

from reviews.constants import USERNAME_REGEX_SIGNS


def validate_username(username):
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
