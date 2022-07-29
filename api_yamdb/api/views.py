from rest_framework import permissions, status, viewsets
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


from .permissions import IsAdmin, IsAuthorOrReadOnly, IsModerator, ReadOnly
from .serializers import (
    CategorySerializer,
    CommentsSerializer,
    CreateTitleSerializer,
    GenreSerializer,
    RegisterDataSerializer,
    ReviewsSerializer,
    TitleSerializer,
    TokenSerializer,
    UserEditSerializer,
    UserSerializer
)

from reviews.models import Category, Comments, Genre, Reviews, Title
from users.models import User


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


class UserViewSet(viewsets.ModelViewSet):
    """Класс пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    search_fields = ('username',)
    lookup_field = "username"

    @action(  # Помимо GET-запроса разрешаем другие методы
        methods=['GET', 'PATCH'],
        detail=False,  # разрешена работа с коллекцией
        url_path="me",  # URL эндпоинта не должен совпадать с именем метода
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):
        """
        Функция обрабатывает 'GET' и 'PATCH' запросы на эндпоинт '/users/me/'
        """
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Возвращаем JSON со всеми данными нового объекта
            # и статус-код 200
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Если данные не прошли валидацию, то возвращаем
        # информацию об ошибках и соответствующий статус-код:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# View-функция register() будет обрабатывать только запросы POST,
# запросы других типов будут отклонены


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Функция обрабатывает POST-запрос для регистрации нового пользователя и
    получаения кода подтверждения, который необходим для получения JWT-токена.
    На вход подается 'username' и 'email', а в ответ происходит отправка
    на почту письма с кодом подтверждения.
    """
    serializer = RegisterDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="YaMDb registration",
        message=f"Your confirmation code: {confirmation_code}",
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """
    Функция обрабатывает POST-запрос для получаения JWT-токена.
    На вход подается 'username' и 'confirmation_code',
    а в ответ формируется JWT-токен.
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )

    if default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
