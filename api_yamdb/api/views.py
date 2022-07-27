from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from .permissions import IsAdmin, IsAuthorOrReadOnly, IsModerator, ReadOnly
from .serializers import (
    CategorySerializer,
    CommentsSerializer,
    CreateTitleSerializer,
    GenreSerializer,
    ReviewsSerializer,
    TitleSerializer
)

from reviews.models import Category, Comments, Genre, Reviews, Title


class CreateListDestroyViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    permission_classes = (IsAdmin | ReadOnly,)
    search_fields = ['name']
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdmin | ReadOnly,)

    queryset = Title.objects.all()

    def get_serializer_class(self):
        if self.action in ('partial_update', 'create'):
            return CreateTitleSerializer
        return TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdmin | IsModerator | IsAuthorOrReadOnly,)

    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdmin | IsModerator | IsAuthorOrReadOnly,)

    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Reviews, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
