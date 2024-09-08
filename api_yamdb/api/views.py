"""Вьюсеты для API."""
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api_yamdb import settings
from reviews.models import User, Category, Title, Genre, Comment, Review
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (
    IsAdminOrReadOnly, IsAdminModeratorAuthorOrReadOnly, AdminOnly
)
from .serializers import (
    TitleReadSerializer, TitleWriteSerializer,
    GenreSerializer, CategorySerializer,
    ReviewSerializer, CommentSerializer,
    UserSerializer, AuthSerializer, TokenSerializer
)


class SignUpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user, created = User.objects.get_or_create(
                    username=request.data.get('username'),
                    email=request.data.get('email')
                )
            except IntegrityError:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                'Код подтверждения',
                f'Ваш код - {confirmation_code}',
                settings.EMAIL_SENDER,
                [request.data.get('email')]
            )
            return Response(
                {'email': serializer.data['email'],
                 'username': serializer.data['username']},
                status=status.HTTP_200_OK)


class GetTokenView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(
                User, username=request.data.get('username')
            )
            if not default_token_generator.check_token(
                    user, request.data.get('confirmation_code')
            ):
                return Response(
                    'Неверный confirmation_code',
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = {'token': str(AccessToken.for_user(user))}
            return Response(token, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['=username']
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated],
            serializer_class=UserSerializer,
            pagination_class=None)
    def me(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            if self.request.method == 'PATCH':
                serializer.validated_data.pop('role', None)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


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

    http_method_names = ['get', 'post', 'delete', 'patch']
    queryset = (
        Title.objects.all().annotate(
            rating=Avg('reviews__score')
        ).order_by('name')
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
        # title.update_rating()

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
