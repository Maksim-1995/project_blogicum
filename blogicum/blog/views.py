from django.shortcuts import render, get_object_or_404

from .models import Post, Category

POSTS_ON_INDEX_PAGE = 5


def index(request):
    """Главная страница: 5 последних опубликованных постов."""
    post_list = Post.objects.get_published_posts().select_related_fields()[
        :POSTS_ON_INDEX_PAGE
    ]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Страница отдельного поста."""
    post = get_object_or_404(
        Post.objects.get_published_posts().select_related_fields(), pk=post_id
    )
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница категории."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    post_list = (
        Post.objects.get_published_posts()
        .select_related_fields()
        .filter(category=category)
    )
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, 'blog/category.html', context)
