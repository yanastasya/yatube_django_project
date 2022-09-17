from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Страница 404 отдаёт кастомный шаблон"""

        response = self.client.get('/nonexist-page/')

        self.assertTemplateUsed(response, 'core/404.html')
