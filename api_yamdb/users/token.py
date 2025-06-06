from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Получение токена доступа для пользователя."""
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
    }
