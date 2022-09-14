from django.contrib.auth import get_user_model
from django.db import models

from .constants import MAX_LENGHT_OF_RETURN_TEXT
from core.models import PubDateModel

User = get_user_model()


class Post(PubDateModel):
    """Модель Post используется для хранения постов в блоге.
    У пользователя есть возможность публиковать посты в общей ленте
    и выбирать тематическую группу, в которой появится его пост.
    """

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:MAX_LENGHT_OF_RETURN_TEXT]


class Group(models.Model):
    """Модель Group для сообществ. Сообщества создаются администратором сайта,
    у посетителей нет возможности их добавлять. При публикации записи автор
    может выбрать одно сообщество и отправить туда свой пост.
    """

    title = models.CharField(
        max_length=200,
        verbose_name="название сообщества",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="уникальный адрес сообщества",
    )
    description = models.TextField(
        verbose_name="описание",
    )

    def __str__(self):
        return self.title


class Comment(PubDateModel):
    """Комментирование постов."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )    

    text = models.TextField(
        verbose_name='Текст комментария',
    )


class Follow(models.Model):
    """Подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписываются',
    )


