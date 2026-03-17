from typing import Optional, Any, Dict
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import QuerySet
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import PostForm, CommentForm, RegistrationForm, ProfileEditForm
from .models import Post, Category, Comment


User = get_user_model()
POSTS_PER_PAGE = 10


class PostListView(ListView):
    """
    Отображает список опубликованных постов на главной странице.

    Поддерживает пагинацию, оптимизированные запросы и подсчёт комментариев.
    Посты сортируются от новых к старым.
    """

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self) -> QuerySet[Post]:
        """
        Возвращает набор опубликованных постов с подгрузкой связанных полей.

        Сортировка по убыванию даты публикации.
        """
        return (
            Post.objects.get_published_posts()
            .select_related_fields()
            .with_comment_count()
        )


class PostDetailView(DetailView):
    """
    Детальная страница поста.

    Проверяет доступность поста для текущего пользователя:
    - Автор видит пост всегда (даже если не опубликован).
    - Остальные пользователи видят только опубликованные посты
    с прошедшей датой и опубликованной категорией.
    На страницу также добавляется форма комментария и список комментариев.
    """

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_queryset(self) -> QuerySet[Post]:
        """Загружает связанные объекты (автор, категория) для всех постов."""
        return Post.objects.available_for_user(
            self.request.user
        ).select_related_fields()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет в контекст форму комментария и список комментариев.

        Отсортированных по дате создания (старые сверху).
        """
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
            .order_by('created_at')
            .all()
        )
        return context


class CategoryPostsView(ListView):
    """
    Отображает список постов определённой категории.

    Категория определяется по slug в URL; учитываются только опубликованные
    категории.
    Посты фильтруются по опубликованности, сортируются от новых к старым.
    """

    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = POSTS_PER_PAGE
    slug_url_kwarg = 'category_slug'

    def get_queryset(self) -> QuerySet[Post]:
        """Получает категорию по slug и возвращает опубликованные посты."""
        self.category = get_object_or_404(
            Category, slug=self.kwargs[self.slug_url_kwarg], is_published=True
        )
        return (
            Post.objects.get_published_posts()
            .select_related_fields()
            .filter(category=self.category)
            .with_comment_count()
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Добавляет объект категории в контекст."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    """
    Профиль пользователя. Показывает список постов выбранного автора.

    - Для владельца профиля отображаются все посты.
    - Для остальных пользователей – только опубликованные посты.
    Сортировка по убыванию даты публикации.
    """

    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self) -> QuerySet[Post]:
        """
        Определяет пользователя по username.

        Возвращает соответствующий набор постов.
        """
        username = self.kwargs.get('username')
        if username is None:
            raise Http404('Не указано имя пользователя в URL')
        self.profile_user = get_object_or_404(User, username=username)
        queryset = Post.objects.select_related_fields().with_comment_count()
        if self.request.user == self.profile_user:
            return queryset.filter(author=self.profile_user)
        return queryset.get_published_posts().filter(author=self.profile_user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавляет объект просматриваемого пользователя в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Редактирование профиля текущего пользователя.

    Доступно только аутентифицированным пользователям.
    """

    model = User
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset: Optional[QuerySet[User]] = None) -> User:
        """Возвращает текущего пользователя для редактирования."""
        return self.request.user

    def get_success_url(self) -> str:
        """После успешного сохранения перенаправляет в профиль пользователя."""
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового поста.

    Только для аутентифицированных пользователей.
    Автором поста автоматически становится текущий пользователь.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form: PostForm) -> HttpResponse:
        """Устанавливает автором текущего пользователя перед сохранением."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """После создания перенаправляет в профиль автора."""
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование поста.

    Доступно только автору поста; если пользователь не автор – редирект на
    страницу поста.
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.available_for_user(self.request.user)

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)

    def get_success_url(self) -> str:
        """После редактирования возвращает на страницу поста."""
        return reverse('blog:post_detail', kwargs={'post_id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление поста.

    Доступно только автору поста;
    если пользователь не автор – редирект на страницу поста.
    """

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_queryset(self):
        return Post.objects.available_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_delete'] = True
        return context

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        return redirect('blog:post_detail', post_id=post.id)

    def get_success_url(self) -> str:
        """После удаления перенаправляет в профиль автора."""
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Создание комментария к посту.

    Только для аутентифицированных пользователей.
    Комментарий привязывается к посту и автору.
    """

    model = Comment
    form_class = CommentForm

    def form_valid(self, form: CommentForm) -> HttpResponse:
        """
        Привязывает комментарий к посту из URL.

        Устанавливает текущего пользователя автором.
        """
        post = get_object_or_404(
            Post.objects.available_for_user(self.request.user),
            pk=self.kwargs['post_id'],
        )
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Возвращает на страницу поста."""
        post_url = reverse(
            'blog:post_detail', kwargs={'post_id': self.object.post.id}
        )
        return f'{post_url}#comment_{self.object.id}'


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование комментария.

    Доступно только автору комментария.
    """

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self) -> bool:
        """Проверяет, является ли текущий пользователь автором комментария."""
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self) -> str:
        """После редактирования возвращает к посту."""
        post_url = reverse(
            'blog:post_detail', kwargs={'post_id': self.object.post.id}
        )
        return f'{post_url}#comment_{self.object.id}'


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление комментария.

    Доступно только автору комментария.
    """

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self) -> bool:
        """Проверяет авторство комментария."""
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self) -> str:
        """После удаления перенаправляет на страницу поста."""
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.object.post.id}
        )


class RegistrationView(CreateView):
    """
    Регистрация нового пользователя.

    Использует встроенный CreateView для создания объекта User через форму
    регистрации.
    После успешной регистрации перенаправляет на страницу входа.
    """

    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')
