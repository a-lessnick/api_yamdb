"""Вьюсеты для API."""
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView

from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

from reviews.models import User, Category, Title, Genre, Comment, Review
from api_yamdb import settings
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (
    IsAdminOrReadOnly, IsAdminModeratorAuthorOrReadOnly, AdminOnly
)
from .serializers import (
    TitleReadSerializer, TitleWriteSerializer,
    GenreSerializer, CategorySerializer,
    ReviewSerializer, CommentSerializer,
    UserSerializer, UserSignUpSerializer, UserReceiveTokenSerializer
)


class UsersViewSet(ModelViewSet):
    """Представление для операций с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False, methods=['GET', 'PATCH'],
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me_data(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateViewSet(APIView):
    """Вьюсет для создания пользователей."""

    permission_classes = (AllowAny,)

    @staticmethod
    def send_confirmation_code(email, username, confirmation_code):
        send_mail(
            subject='Доступ к API',
            message=(
                f'{username}, Ваш \n'
                f'код подтверждения для доступа к API: {confirmation_code}'
            ),
            recipient_list=(email,),
            from_email=settings.EMAIL_SENDER,
            fail_silently=True,
        )

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        email = request.data.get('email')

        user, _ = User.objects.get_or_create(
            username=username,
            email=email
        )

        self.send_confirmation_code(
            user.email,
            username,
            default_token_generator.make_token(user)
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

        # if User.objects.filter(username=username, email=email).exists():
        #     user = User.objects.get(username=username, email=email)
        #     self.send_confirmation_code(
        #         user.email,
        #         username,
        #         default_token_generator.make_token(user)
        #     )
        #     serializer = UserSignUpSerializer(data=request.data)
        #     serializer.is_valid()
        #     return Response(
        #         serializer.data,
        #         status=status.HTTP_200_OK
        #     )
        # serializer = UserSignUpSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # user = User.objects.create(**serializer.validated_data)
        # self.send_confirmation_code(
        #     user.email,
        #     username,
        #     default_token_generator.make_token(user)
        # )



class UserReceiveTokenViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    """Вьюсет для получения токена."""

    queryset = User.objects.all()
    serializer_class = UserReceiveTokenSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = UserReceiveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': 'Неверный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=status.HTTP_200_OK
        )


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет для создания объектов класса Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет для создания объектов класса Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов класса Title."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = (
        Title.objects.all().annotate(Avg('reviews__score')).order_by('name')
    )
    serializer_class = TitleWriteSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer

    def update(self, request, *args, **kwargs):
        """Обновление произведения."""
        from rest_framework import exceptions
        raise exceptions.MethodNotAllowed(request.method)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        """Возвращает отзывы для конкретного произведения."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Создаёт новый отзыв и устанавливает автора и произведение."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)
        title.update_rating()

    def get_title(self):
        """Возвращает произведение по идентификатору."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями к отзывам."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        """Возвращает комментарии для конкретного отзыва."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        """Создаёт новый комментарий и устанавливает автора."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
