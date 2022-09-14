from django.core.paginator import Paginator

from .constants import NUMBER_OF_POSTS_ON_PAGE


def get_page(request, post_list):
    """Пагинатор для страниц с выводом списка постов."""

    paginator = Paginator(post_list, NUMBER_OF_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
