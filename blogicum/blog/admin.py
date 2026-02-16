from django.contrib import admin

from .models import Category, Location, Post


class CategoryAdmin(admin.ModelAdmin):
    """Настройки отображения модели Category в админке."""

    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


class LocationAdmin(admin.ModelAdmin):
    """Настройки отображения модели Location в админке."""

    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published',)


class PostAdmin(admin.ModelAdmin):
    """Настройки отображения модели Post в админке."""

    list_display = (
        'title',
        'pub_date',
        'author',
        'category',
        'location',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'text')
    list_filter = ('is_published', 'category', 'location')
    date_hierarchy = 'pub_date'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
