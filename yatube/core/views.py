from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Функция обработки ошибки 404."""

    template = 'core/404.html'
    context = {'path': request.path}

    return render(request, template, context, status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    """Функция обработки ошибки 403csrf."""

    template = 'core/403csrf.html'
    return render(request, template)


def server_error(request):
    """Функция обработки ошибки 500."""

    template = 'core/500.html'
    return render(request, template, HTTPStatus.INTERNAL_SERVER_ERROR)


def permission_denied(request, exception):
    """Функция обработки ошибки 403."""

    template = 'core/403.html'
    return render(request, template, HTTPStatus.FORBIDDEN)
