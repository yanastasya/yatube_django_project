from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow
from .utils import get_page
from .constants import CASH_TIME_SEC


@cache_page(CASH_TIME_SEC, key_prefix='index_page')
def index(request):
    """Главная страница."""

    template = 'posts/index.html'
    post_list = Post.objects.select_related('group', 'author').all()
    page_obj = get_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    """Страница сообщества."""

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_obj = get_page(request, post_list)

    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    """Персональная страница пользователя."""

    template = 'posts/profile.html'
    author = User.objects.get(username=username)
    post_list = author.posts.select_related('group')
    page_obj = get_page(request, post_list)

    following = (
        request.user.is_authenticated
        and request.user != author
        and Follow.objects.filter(user=request.user, author=author).exists()
    )

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }

    return render(request, template, context)


def post_detail(request, post_id):
    """Страница просмотра отдельного поста."""

    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related(
            'group',
            'author'
        ), id=post_id
    )
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, template, context)


@login_required
def post_create(request):
    """Страница для создания новой записи."""

    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()

        return redirect('posts:profile', request.user)

    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Страница для редактирования поста."""

    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        form.save()

        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }

    return render(request, template, context)


@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post.id)


@login_required
def follow_index(request):
    """Страница с лентой постов авторов, на которых подписан пользователь."""

    template = 'posts/follow.html'

    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(request, post_list)
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""

    author = get_object_or_404(User, username=username)
    if not (
        request.user == author
        or Follow.objects.filter(user=request.user, author=author).exists()
    ):
        Follow.objects.create(user=request.user, author=author)

    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""

    author = get_object_or_404(User, username=username)

    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:profile', username)
