from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Класс для обработки страницы с информацией об авторе проекта."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Класс для обработки страницы с информацией о технологиях,
    использованных в проекте.
    """

    template_name = 'about/tech.html'
