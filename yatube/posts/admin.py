from django.contrib import admin

from .models import Group, Post, Follow


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


admin.site.register(Group)
admin.site.register(Follow)
