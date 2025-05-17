import re

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api import constants
from reviews.models import Category, Comments, Genre, Review, Title
from reviews.validators import validate_title_year

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации и входа пользователей."""

    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_email(self, value):
        if len(value) > constants.EMAIL_MAX_LENGTH:
            raise serializers.ValidationError(
                'Email не может быть более '
                f'{constants.EMAIL_MAX_LENGTH} символов.'
            )
        return value

    def validate_username(self, value):
        pattern = re.compile(constants.USERNAME_CHECK)
        if not pattern.match(value):
            raise serializers.ValidationError(
                'Username может состоять из букв, цифр, точки, @, + или -'
            )
        if value == constants.NOT_ALLOWED_USERNAME:
            raise serializers.ValidationError(
                'Использование имени пользователя '
                f'{constants.NOT_ALLOWED_USERNAME} запрещено!'
            )
        if len(value) > constants.USERNAME_MAX_LENGTH:
            raise serializers.ValidationError(
                'Username не может быть более '
                f'{constants.USERNAME_MAX_LENGTH} символов.'
            )
        return value

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        if User.objects.filter(username=username, email=email).exists():
            return attrs
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': ['Имя уже занято!']}
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': ['Пользователь с таким email уже существует!']}
            )
        return attrs

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        user, created = User.objects.get_or_create(
            username=username,
            email=email
        )
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Сериализатор для получения пользователями токена доступа."""

    username = serializers.RegexField(
        regex=constants.USERNAME_CHECK,
        max_length=constants.USERNAME_MAX_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        required=True,
        max_length=constants.CONFIRMATION_CODE_LENGTH,
    )


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        allow_null=False,
        required=True,
        allow_empty=False
    )
    year = serializers.IntegerField(validators=[validate_title_year])

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category',
        )
        model = Title

    def to_representation(self, instance):
        """Метод для вывода информации как при гет-запросе."""
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов на произведение."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(
        max_value=constants.MAX_SCORE_VALUE,
        min_value=constants.MIN_SCORE_VALUE
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate(self, data):
        request = self.context['request']
        if (
            request.method == 'POST'
            and Review.objects.filter(
                title=get_object_or_404(
                    Title,
                    pk=self.context.get('view').kwargs.get('title_id')
                ),
                author=request.user
            ).exists()
        ):
            raise serializers.ValidationError(
                'Может существовать только один отзыв!'
            )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев на отзывы."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
