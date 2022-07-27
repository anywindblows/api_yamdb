from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenresViewSet,
    ReviewsViewSet,
    TitleViewSet
)

v1_router = SimpleRouter()
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

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
