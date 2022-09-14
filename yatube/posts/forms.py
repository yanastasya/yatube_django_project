from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма создания комментария к посту."""

    class Meta:
        model = Comment
        fields = ('text',)
