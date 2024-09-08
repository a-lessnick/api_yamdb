"""Сериализаторы."""
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers

from reviews.models import User, Category, Comment, Genre, Review, Title
from reviews.constants import USERNAME_REGEX_SIGNS, NAME_MAX_LENGTH


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        ordering = ['id']
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(
        required=True, max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' недопустимо.")
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


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
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')

        if request.method == 'POST':
            if Review.objects.filter(
                author=author, title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    'Нельзя оставить два отзыва на одно произведение.'
                )
        elif request.method in ['PATCH', 'PUT']:
            if self.instance.author == author:
                review_id = self.instance.id
                existing_review = Review.objects.filter(
                    author=author, title_id=title_id
                ).exclude(id=review_id)
                if existing_review.exists():
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
