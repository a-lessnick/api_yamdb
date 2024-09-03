from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.models import User, Category, Comment, Genre, Review, Title


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=[User.REGEX_SIGNS]
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


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


class SignUpSerializer(serializers.ModelSerializer):

    def validate(self, user_data):
        email = user_data.get('email')
        username = user_data.get('username')

        if User.objects.filter(email=email).exists():
            if User.objects.filter(username=username).exists():
                return user_data
            raise ValidationError(f'Email {email} уже существует')

        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username {username} уже существует')
        return user_data

    class Meta:
        model = User
        fields = ('username', 'email')


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
