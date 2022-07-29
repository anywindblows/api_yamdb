from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField(
        validators=[
            MaxValueValidator(timezone.now().year)
        ]
    )
    description = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        related_name='titles',
        on_delete=models.SET_NULL,
    )

    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
      
    class Meta:
        verbose_name = 'Тайтл'
        verbose_name_plural = 'Тайтлы'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'year'],
                name='unique_title'
            )
        ]

    def __str__(self):
        return self.name


class Reviews(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_reviewing',
            ),
        )

    def __str__(self):
        return f'{self.title} {self.text} {self.author} {self.score}'


class Comments(models.Model):
    review = models.ForeignKey(Reviews, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author} {self.text}'
