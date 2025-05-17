from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from api import constants
from users.validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICES = (
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Админ'),
    )

    role = models.CharField(
        max_length=constants.ROLE_MAX_LENGTH,
        choices=CHOICES,
        default=USER,
        verbose_name='Уровень доступа пользователя',
        help_text='Уровень доступа пользователя'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Заметка о пользователе',
        help_text='Напишите заметку о себе'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта пользователя',
        help_text='Введите свой электронный адрес'
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=(
            'Обязательное поле. 150 символов или меньше. '
            'Только буквы, цифры и @/./+/-/_ символы.'
        ),
        validators=[
            validate_username,
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    'Имя пользователя может содержать только '
                    'буквы, цифры и @/./+/-/_ символы.'
                ),
            ),
        ],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
        verbose_name='Имя пользователя',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email'
            ),
        )

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff
