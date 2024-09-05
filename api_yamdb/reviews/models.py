from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Avg

from api_yamdb.settings import TEXT_FIELD_LENGTH, SLUG_FIELD_LENGTH


class User(AbstractUser):
    REGEX_SIGNS = r'^[\w.@+-]+\Z'
    REGEX_ME = r'[^m][^e]'
    NAME_MAX_LENGTH = 150
    EMAIL_MAX_LENGTH = 254
    ROLE_MAX_LENGTH = 64

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
        validators=(RegexValidator(REGEX_SIGNS), RegexValidator(REGEX_ME)),
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
    name = models.CharField('Название', max_length=TEXT_FIELD_LENGTH)
    year = models.IntegerField('Год выхода')
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(
        Genre, through='TitleGenre', verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Категория'
    )
    rating = models.IntegerField('Рейтинг', default=None, null=True)

    def update_rating(self):
        rating = self.reviews.aggregate(Avg('score'))['score__avg']
        self.rating = rating
        self.save()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    """Модель отзыва на произведение."""

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
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True,
    )

    def save(self, *args, **kwargs):
        """Сохраняет отзыв и обновляет рейтинг после его публикации."""
        super().save(*args, **kwargs)
        self.title.update_rating()

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
    """Модель комментария к отзыву."""

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
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.author
