import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reviews.models import Category, Comments, Genre, Review, Title, GenreTitle

User = get_user_model()

MODELS = {
    'User': User,
    'Category': Category,
    'Genre': Genre,
    'Title': Title,
    'GenreTitle': GenreTitle,
    'Review': Review,
    'Comments': Comments,
}
PROCEDURE = [
    'User',
    'Category',
    'Genre',
    'Title',
    'GenreTitle',
    'Review',
    'Comments'
]
HEADERS = [
    'genre',
    'category',
    'title',
    'review',
]


class Command(BaseCommand):
    """
    Импорт данных из файлов *.csv в директории в БД.
    Импортирует все данные из всех файлов, находящихся в директории.
    Файлы должны иметь название, такое же, как и таблица БД,
    в которую импортируются данные.
    Константа PROCEDURE определяет порядок импорта.
    Константа HEADERS определяет поля БД с внешним ключем.
    """

    help = 'Импорт данных из директории, importcsv <путь к директории>.'

    def add_arguments(self, parser):
        parser.add_argument(
            'dir', type=str,
            help='Папка с файлами для импорта данных'
        )

    def get_model_file(self, dir):
        """Чтение директории и составление словаря Модель - Файл."""
        list_dir = os.listdir(dir)
        model_file = {}
        for file in list_dir:
            name = file.split('.')
            model = name[0]
            model_file[model] = file
        return model_file

    def prepare_row(self, data):
        """Подготовка данных для создания объекта."""
        for header, value in data.items():
            try:
                if header == 'author':
                    data[header] = User.objects.get(id=value)
                elif header in HEADERS:
                    data[header] = MODELS[
                        header.capitalize()
                    ].objects.get(id=value)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Объект {data[header]}={value} не '
                        f'существует. Ошибка: {e}.\n'
                    )
                )
                continue
        return data

    def create_models_object(self, model, data):
        """Создание объекта модели."""
        if model == 'User':
            obj = User.objects.create_user(**data)
        else:
            obj, st = MODELS[
                model
            ].objects.get_or_create(**data)
        self.stdout.write(
            self.style.SUCCESS(
                f'Объект {obj} создан.'
            )
        )

    def handle(self, *args, **kwargs):
        dir = kwargs['dir']
        model_file = self.get_model_file(dir)
        try:
            for operation in PROCEDURE:
                file = model_file[operation]
                with open(dir + file, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        row = self.prepare_row(row)
                        try:
                            self.create_models_object(operation, row)
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'При импорте в модели {operation} '
                                    f'произошла ошибка: {e}.\n'
                                    f'Проверьте данные {file}: {row}'
                                )
                            )
                            continue
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'При импорте в модели {operation} произошла ошибка {e}.'
                )
            )