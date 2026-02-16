from django.db import models
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    """
    Кастомный QuerySet для модели Post.

    Содержит методы для часто используемых фильтраций и оптимизаций запросов.
    """

    def get_published_posts(self):
        """Возвращает опубликованные посты с учетом всех условий."""
        return self.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    def select_related_fields(self):
        """Оптимизирует запрос, загружая объекты одним SQL-запросом."""
        return self.select_related('category', 'location', 'author')
