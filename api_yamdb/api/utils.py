from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.generics import get_object_or_404

User = get_user_model()


def send_confirmation_code_to_email(username):
    """
    Отправка пользователю кода подтверждения
    для получения токена доступа.
    """
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтвержения для завершения регистрации',
        f'Ваш код для получения JWT токена {confirmation_code}',
        settings.ADMIN_EMAIL,
        (user.email,),
        fail_silently=False,
    )
    user.save()
