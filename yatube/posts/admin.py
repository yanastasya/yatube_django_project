from django.contrib import admin

from .models import Group, Post, Follow, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Класс для настройки отображения данных о постах
    в интерфейсе администратора.
    """

    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс для настройки отображения данных о подписках
    в интерфейсе администратора.
    """

    list_display = ('pk', 'author', 'user',)
    search_fields = ('author', 'user',)
    list_filter = ('author', 'user',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Класс для настройки отображения данных о подписках
    в интерфейсе администратора.
    """

    list_display = ('pk', 'post', 'author', 'text', 'pub_date',)
    search_fields = ('text', 'author', 'post',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Group)
