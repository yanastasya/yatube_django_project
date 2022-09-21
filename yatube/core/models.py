from django.db import models


class TextAndPubDateModel(models.Model):
    """Абстрактная модель. Добавляет дату создания и текст."""

    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    text = models.TextField(
        'Текст',
    )

    class Meta:
        abstract = True
