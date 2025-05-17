import datetime as dt

from django.core.exceptions import ValidationError


def validate_title_year(value):
    """Валидатор для года создания произведения."""
    year = dt.date.today().year
    if not (value <= year):
        raise ValidationError('Некоректный год.')
    return value
