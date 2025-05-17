from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet, CommentsViewSet, GenreViewSet, ReviewViewSet,
    TitleViewSet, UsersViewSet, get_token, signup,
)

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)
router_v1.register('users', UsersViewSet, basename='users')

auth_patterns = [
    path('signup/', signup, name='user-registration'),
    path('token/', get_token, name='user_get_token'),
]

api_v1_patterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('v1/', include(api_v1_patterns)),
]
