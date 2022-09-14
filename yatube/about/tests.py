from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    """Страницы /about/author/ и /about/tech/
    доступны любому пользователю.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности адресов страниц /about/author/
        и /about/tech/ для любого пользователя.
        """

        urls_and_status = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }

        for address, status in urls_and_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_views_about_pages_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:author,
        about:tech доступны.
        """

        url_and_names = {
            'about:author': '/about/author/',
            'about:tech': '/about/tech/',
        }
        for name, address in url_and_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_views_about_page_uses_correct_template(self):
        """При запросе к about:author и about:tech
        применяется  соответствующие шаблоны."""

        templates_and_names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }

        for name, templates in templates_and_names.items():
            with self.subTest(templates=templates):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, templates)
