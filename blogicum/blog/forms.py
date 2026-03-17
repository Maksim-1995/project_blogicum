from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования постов.

    Исключает поля author, is_published и created_at, так как они
    заполняются автоматически или не должны редактироваться пользователем.
    Для поля pub_date используется виджет datetime-local для удобного ввода
    даты и времени.
    """

    class Meta:
        model = Post
        exclude = ('author', 'is_published', 'created_at')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """
    Форма для добавления и редактирования комментариев.

    Содержит только поле text; остальные поля (post, author, created_at)
    заполняются автоматически в представлении. Поле text отображается как
    текстовое поле высотой в 3 строки.
    """

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class RegistrationForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.

    Наследуется от UserCreationForm, добавляя поля email, first_name,
    last_name.
    Пароль и подтверждение пароля уже включены в родительскую форму.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class ProfileEditForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя.

    Позволяет пользователю изменить имя пользователя, email, имя и фамилию.
    Используется в ProfileEditView.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
