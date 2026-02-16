from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedModel
from .querysets import PostQuerySet


User = get_user_model()


class Category(PublishedModel):
    """
    Модель для тематических категорий постов.

    Наследуется от PublishedModel, получая поля is_published и created_at.
    """

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedModel):
    """
    Модель для географических меток (местонахождение постов).

    Наследуется от PublishedModel, получая поля is_published и created_at.
    """

    name = models.CharField(max_length=256, verbose_name='Название места')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(PublishedModel):
    """
    Модель для публикаций (постов) в блоге.

    Наследуется от PublishedModel, получая поля is_published и created_at.
    """

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
    )
    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_location_display(self):
        """
        Метод для получения отображаемого названия локации.

        Возвращает название локации или 'Планета Земля'.
        """
        if self.location:
            return self.location.name
        return 'Планета Земля'

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
