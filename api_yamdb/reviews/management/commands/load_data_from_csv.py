import csv
import logging
import sys

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError

from reviews.models import (
    Category, Comment, Genre, Review, Title, User
)
TABLES_FILES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    # TitleGenre: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}

FK_FIELDS = {
    'category': ('category', Category),
    'title_id': ('title', Title),
    'genre_id': ('genre', Genre),
    'author': ('author', User),
    'review_id': ('review', Review),
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def convert_foreign_key(csv_data):
    """Конвертер значений для Foreign Key полей."""
    csv_data_converted = csv_data.copy()
    for field_key, field_value in csv_data.items():
        if field_key in FK_FIELDS.keys():
            table_key = FK_FIELDS[field_key][0]
            csv_data_converted[table_key] = (
                FK_FIELDS[field_key][1].objects.get(pk=field_value)
            )
    return csv_data_converted


def load_from_csv(table, file_name):
    """Загрузка данных csv-файлов."""
    error_message = f'Таблица {table.__qualname__} не загружена.'
    success_message = f'Таблица {table.__qualname__} загружена.'

    file_path = f'{settings.BASE_DIR}/static/data/{file_name}'

    with (open(file_path, 'r', encoding='utf-8')) as csv_file:
        reader = list(csv.reader(csv_file))
        rows = reader[1:]
        for row in rows:
            csv_data = convert_foreign_key(dict(zip(reader[0], row)))
            try:
                model = table(**csv_data)
                model.save()
            except (ValueError, IntegrityError) as err:
                logger.error(
                    f'Ошибка в загружаемых данных. {err}. '
                    f'{error_message}'
                )
                break
        logger.debug(success_message)


class Command(BaseCommand):
    """Класс загрузки тестовой базы данных."""

    def handle(self, *args, **options):
        for table, file_name in TABLES_FILES.items():
            print(f'Загрузка таблицы {table.__qualname__}')
            load_from_csv(table, file_name)

        self.stdout.write(self.style.SUCCESS('Данные загружены в БД.'))
