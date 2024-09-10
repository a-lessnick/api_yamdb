"""Сериализаторы."""
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers

from reviews.constants import (
    EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, USERNAME_REGEX_SIGNS
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        ordering = ['id']
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=EMAIL_MAX_LENGTH)
    username = serializers.CharField(
        required=True, max_length=NAME_MAX_LENGTH,
        validators=[RegexValidator(
            regex=USERNAME_REGEX_SIGNS,
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
        many=True,
        allow_null=False,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, title):
        """Определение сериализатоа для чтения."""
        serializer = TitleReadSerializer(title)
        return serializer.data


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для методов чтения произведений."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

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
        if request.method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(
                title__id=title_id, author=request.user
        ).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв о данном произведении.'
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
