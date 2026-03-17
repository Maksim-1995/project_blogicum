from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """
    Отображает страницу «О проекте» (about.html).

    Использует встроенный TemplateView для рендеринга статического шаблона.
    """

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """
    Отображает страницу «Правила» (rules.html).

    Использует встроенный TemplateView для рендеринга статического шаблона.
    """

    template_name = 'pages/rules.html'


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    Кастомный обработчик ошибки 404 (страница не найдена).

    Возвращает HTTP-ответ со статусом 404 и отображает шаблон pages/404.html.
    """
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    """
    Кастомный обработчик ошибки CSRF 403.

    Возвращает HTTP-ответ со статусом 403 и отображает шаблон
    pages/403csrf.html.
    Параметр reason содержит причину ошибки (по умолчанию пустая строка).
    """
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request: HttpRequest) -> HttpResponse:
    """
    Кастомный обработчик ошибки 500 (внутренняя ошибка сервера).

    Возвращает HTTP-ответ со статусом 500 и отображает шаблон pages/500.html.
    """
    return render(request, 'pages/500.html', status=500)
