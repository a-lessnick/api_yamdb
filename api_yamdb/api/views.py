from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly, IsAdminModeratorAuthorOrReadOnly
from reviews.models import User, Category, Title, Genre, Comment, Review
from .serializers import (
    GetTokenSerializer, SignUpSerializer,
    TitleReadSerializer, TitleWriteSerializer,
    GenreSerializer, CategorySerializer,
    ReviewSerializer, CommentSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    @action(methods=['POST'], detail=False, url_path='token')
    def get_token(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid()
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if default_token_generator.check_token(
                user,
                data.get('confirmation_code')
        ):
            access_token = RefreshToken.for_user(user).access_token
            return Response(
                {'token': str(access_token)},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_mail_confirmation_code(user, confirmation_code):
        send_mail(
            subject='Доступ к API',
            message=(
                f'{user.username}, Ваш \n'
                f'код подтверждения для доступа к API: {confirmation_code}'
            ),
            recipient_list=[user.email],
            from_email='practicum@yandex.com',
            fail_silently=True,
        )

    @action(methods=['POST'], detail=False, permission_classes=(AllowAny,), url_path='signup')
    def signup(self, request):
        user = User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        )
        if not user:
            serializer = SignUpSerializer(data=request.data)
            serializer.is_valid()
            user = serializer.save()
            confirmation_code = default_token_generator.make_token(user)
            AuthViewSet.send_mail_confirmation_code(user, confirmation_code)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = SignUpSerializer(user[0])
        confirmation_code = default_token_generator.make_token(user[0])
        AuthViewSet.send_mail_confirmation_code(user[0], confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateListDestroyViewset(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет класс для создания и удаления."""

    serializer_class = None
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)


class CategoryViewSet(CreateListDestroyViewset):
    """Вьюсет для создания объектов класса Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewset):
    """Вьюсет для создания объектов класса Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания объектов класса Title."""

    queryset = (
        Title.objects.all().annotate(Avg('reviews__score')).order_by('name')
    )
    serializer_class = TitleWriteSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    queryset = Review.objects.all()

    def get_queryset(self):
        """Возвращает отзывы для конкретного произведения."""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        """Создаёт новый отзыв и устанавливает автора и произведение."""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
        title.update_rating()

    def perform_update(self, serializer):
        """Обновляет отзыв и пересчитывает рейтинг произведения."""
        super().perform_update(serializer)
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        title.update_rating()

    def perform_destroy(self, instance):
        """Удаляет отзыв и пересчитывает рейтинг произведения."""
        title = instance.title
        super().perform_destroy(instance)
        title.update_rating()


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями к отзывам."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    queryset = Comment.objects.all()

    def get_queryset(self):
        """Возвращает комментарии для конкретного отзыва."""
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        """Создаёт новый комментарий и устанавливает автора."""
        serializer.save(author=self.request.user,
                        review_id=self.kwargs.get('review_id'))
