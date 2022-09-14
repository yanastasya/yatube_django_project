from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Фильтр, передающий параметры с перечнем HTML-атрибутов,
    которые нужно изменить.
    """

    return field.as_widget(attrs={'class': css})
