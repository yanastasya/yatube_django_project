import datetime as dt


def year(request):
    """Функция возвращает текущий год."""

    return {
        'year': dt.datetime.today().year,
    }
