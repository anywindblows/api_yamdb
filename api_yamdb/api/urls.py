from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenresViewSet,
    ReviewsViewSet,
    TitleViewSet,
    UserViewSet,
    get_jwt_token,
    register
)

v1_router = DefaultRouter()
v1_router.register(r'genres', GenresViewSet, basename='genres')
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(
    r'titles', TitleViewSet,
    basename='title'
)
v1_router.register(
    r'^titles/(?P<title_id>\d+)/reviews', ReviewsViewSet,
    basename='reviews'
)
v1_router.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
v1_router.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/signup/', register, name='register'),
    path('v1/auth/token/', get_jwt_token, name='token')
]
