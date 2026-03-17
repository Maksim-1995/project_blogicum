from django.db import models
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    """
    Кастомный QuerySet для модели Post.

    Содержит методы для часто используемых фильтраций и оптимизаций запросов.
    """

    def published_condition(self):
        """Возвращает Q-объект с условиями для опубликованных постов."""
        return models.Q(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    def get_published_posts(self):
        """Возвращает опубликованные посты с учетом всех условий."""
        return self.filter(self.published_condition())

    def select_related_fields(self):
        """Оптимизирует запрос, загружая объекты одним SQL-запросом."""
        return self.select_related('category', 'location', 'author')

    def with_comment_count(self):
        """
        Возвращает посты с количеством комментариев.

        Отсортированные по дате публикации (новые сверху).
        """
        return self.annotate(comment_count=models.Count('comments')).order_by(
            '-pub_date'
        )

    def for_author(self, author):
        """Возвращает все посты автора (без фильтрации по опубликованности)."""
        return self.filter(author=author)

    def available_for_user(self, user):
        """
        Возвращает посты, доступные для просмотра указанному пользователю.

        Для автора — все его посты (без фильтрации по опубликованности).
        Для остальных — только опубликованные посты.
        """
        if not user.is_authenticated:
            return self.filter(self.published_condition())
        condition = models.Q(author=user) | self.published_condition()
        return self.filter(condition)
