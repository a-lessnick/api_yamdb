"""Модели приложения reviews."""
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator, MinValueValidator
)
from django.db import models

from .constants import (
    TEXT_FIELD_LENGTH, SLUG_FIELD_LENGTH,
    SCORE_MIN_VALUE, SCORE_MAX_VALUE,
    NAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
    ROLE_MAX_LENGTH,
)
from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
    ]

    username = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
        validators=(validate_username,),
        verbose_name='Никнейм пользователя',
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name='E-mail пользователя',
    )
    first_name = models.CharField(
        blank=True,
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=NAME_MAX_LENGTH,
        verbose_name='Фамилия пользователя',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя',
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        blank=True,
        max_length=ROLE_MAX_LENGTH,
        verbose_name='Роль пользователя',
    )

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Genre(models.Model):
    """Жанры произведений."""

    name = models.CharField('Название', max_length=TEXT_FIELD_LENGTH)
    slug = models.SlugField(
        'Слаг жанра', unique=True, max_length=SLUG_FIELD_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Категории произведений."""

    name = models.CharField('Название', max_length=TEXT_FIELD_LENGTH)
    slug = models.SlugField(
        'Слаг категории', unique=True, max_length=SLUG_FIELD_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения."""

    name = models.CharField('Название', max_length=TEXT_FIELD_LENGTH)
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name='genres')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Категория'
    )

    year = models.SmallIntegerField(
        verbose_name='Год выпуска',
        validators=[
            MinValueValidator(
                0,
                message='Значение года не может быть отрицательным'
            ),
            MaxValueValidator(
                int(datetime.now().year),
                message='Значение года не может быть больше текущего'
            )
        ],
        db_index=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(SCORE_MIN_VALUE),
            MaxValueValidator(SCORE_MAX_VALUE)
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # self.title.update_rating()

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique_review'
            )
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Ревью',
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.author
