from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
)
from rest_framework.response import Response

from api.filters import FilterTitle
from api.mixins import ModelMixinSet
from api.permissions import (
    IsAdminModeratorAuthorOrReadOnly, IsAdminOrStaff, IsAdminUserOrReadOnly,
)
from api.serializers import (
    AuthTokenSerializer, CategorySerializer, CommentsSerializer,
    GenreSerializer, ReviewSerializer, SignUpSerializer, TitleReadSerializer,
    TitleWriteSerializer, UserSerializer,
)
from api.utils import send_confirmation_code_to_email
from reviews.models import Category, Genre, Review, Title
from users.token import get_tokens_for_user

User = get_user_model()


@api_view(('POST',))
@permission_classes((AllowAny,))
def signup(request):
    """
    Представление для отправки на email пользователям кода поддверждения.
    Доступно всем пользователям.
    Предусмотрены только POST-запросы.
    Принимает username и email.
    Отправляет пользвателю сгенерированный код подтверждения.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    send_confirmation_code_to_email(request.data.get('username'))
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes((AllowAny,))
def get_token(request):
    """
    Представление для получения пользователем токена доступа.
    Доступно всем пользователям.
    Предусмотрены только POST-запросы.
    Принимает username и confirmation_code.
    Отправляет пользвателю обновленный access токен.
    """
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    confirmation_code = serializer.data.get('confirmation_code')
    if default_token_generator.check_token(user, confirmation_code):
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ModelMixinSet):
    """
    Представление для категорий произведений.
    На чтение доступно всем пользователям.
    Создание, изменение, удаление доступно только администраторам.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ModelMixinSet):
    """
    Представление для жанров произведений.
    На чтение доступно всем пользователям.
    Создание, изменение, удаление доступно только администраторам.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    Представление для произведений.
    На чтение доступно всем пользователям.
    Создание, изменение, удаление доступно только администраторам.
    """

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('rating')
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = ['name', 'category', 'genre', 'year', 'rating']
    ordering = ['rating']
    filterset_class = FilterTitle
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Представление для отзывов на произведения.
    На чтение доступно всем пользователям.
    Создание, изменение, удаление доступно
    только администраторам и модераторам.
    """

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly, )
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Представление для комментариев на отзывы.
    На чтение доступно всем пользователям.
    Создание, изменение, удаление доступно
    только администраторам и модераторам.
    """

    serializer_class = CommentsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly, )
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


class UsersViewSet(viewsets.ModelViewSet):
    """
    Представление для работы с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrStaff,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete',)

    @action(
        methods=('get', 'patch',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
