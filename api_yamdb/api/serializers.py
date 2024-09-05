"""Сериализаторы."""
from rest_framework import serializers

from reviews.models import User, Category, Comment, Genre, Review, Title


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username in 'me':
            raise serializers.ValidationError(
                '"me" запрещено использовать!'
            )
        return username


class UserReceiveTokenSerializer(serializers.Serializer):
    """Сериализатор получения токена."""

    username = serializers.RegexField(
        regex=User.REGEX_SIGNS,
        max_length=User.NAME_MAX_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=User.NAME_MAX_LENGTH,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, username):
        if username in 'me':
            raise serializers.ValidationError(
                '"me" запрещено использовать!'
            )
        return username


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class NotAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей не являющихся Админом."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанров произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категорий произведений."""
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для методов записи/обновления/удаления произведений."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для методов чтения произведений."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('genre', 'rating')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов о произведениях."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверяет уникальность отзыва пользователя на одно произведение."""
        request = self.context.get('request')
        if request.method == 'POST':
            author = request.user
            title_id = self.context.get('view').kwargs.get('title_id')
            if Review.objects.filter(
                author=author, title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    'Нельзя оставить два отзыва на одно произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
