from http import HTTPStatus

from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorized_client_1 = Client()
        cls.user_1 = User.objects.create_user(username='TestUser1')
        cls.authorized_client_1.force_login(cls.user_1)

        cls.authorized_client_2 = Client()
        cls.user_2 = User.objects.create_user(username='TestUser2')
        cls.authorized_client_2.force_login(cls.user_2)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост',
            group=cls.group,
        )

        cls.PAGES_URLS = {
            'index': '/',
            'group_list': f'/group/{cls.group.slug}/',
            'profile': f'/profile/{cls.post.author.username}/',
            'post_detail': f'/posts/{cls.post.id}/',
            'post_create': '/create/',
            'post_edit': f'/posts/{cls.post.id}/edit/',
            'add_comment': f'/posts/{cls.post.id}/comment/',
            'follow_index': '/follow/',
            'profile_follow': f'/profile/{cls.post.author.username}/follow',
            'profile_unfollow': (
                f'/profile/{cls.post.author.username}/unfollow'
            ),
            'unusing_page': '/unusing_page/'
        }

    def setUp(self):
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны для страниц."""

        self.URL_TEMPLATES_NAMES = {
            self.PAGES_URLS['index']: 'posts/index.html',
            self.PAGES_URLS['group_list']: 'posts/group_list.html',
            self.PAGES_URLS['profile']: 'posts/profile.html',
            self.PAGES_URLS['post_detail']: 'posts/post_detail.html',
            self.PAGES_URLS['post_create']: 'posts/create_post.html',
            self.PAGES_URLS['post_edit']: 'posts/create_post.html',
            self.PAGES_URLS['follow_index']: 'posts/follow.html',
        }

        for address, template in self.URL_TEMPLATES_NAMES.items():
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertTemplateUsed(
                    response, template)

    def test_urls_exists_for_guest(self):
        """Страницы  index, group_list, profile, post_detail,
        доступны любому пользователю, страница с несуществующим адресом
        - возвращает ошибку 404.
        """
        self.URLS_AND_STATUS_PAGES_FOR_GUEST_CLIENT = {
            self.PAGES_URLS['index']: HTTPStatus.OK,
            self.PAGES_URLS['group_list']: HTTPStatus.OK,
            self.PAGES_URLS['profile']: HTTPStatus.OK,
            self.PAGES_URLS['post_detail']: HTTPStatus.OK,
            self.PAGES_URLS['unusing_page']: HTTPStatus.NOT_FOUND,
        }

        for address, status in (
            self.URLS_AND_STATUS_PAGES_FOR_GUEST_CLIENT.items()
        ):
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_exists_for_authorized(self):
        """Страница post_create, follow_index доступна любому
        авторизованному пользователю; cтраница post_edit
        доступна только автору поста.
        """

        self.URLS_AND_STATUS_PAGES_FOR_AUTHORIZED_CLIENT = {
            self.PAGES_URLS['post_create']: (HTTPStatus.OK),
            self.PAGES_URLS['post_edit']: (HTTPStatus.OK),
            self.PAGES_URLS['follow_index']: (HTTPStatus.OK),
        }

        for address, status in (
            self.URLS_AND_STATUS_PAGES_FOR_AUTHORIZED_CLIENT.items()
        ):
            with self.subTest(address=address):
                response = self.authorized_client_1.get(address)
                self.assertEqual(response.status_code, status)

    def test_urls_redirect_not_author_on_post_detail(self):
        """При запросе  авторизованным пользователем страницы post_edit,
        перенаправляет на страницу post_detail, если он не автор.
        """

        response = self.authorized_client_2.get(
            self.PAGES_URLS['post_edit'],
            follow=True
        )
        self.assertRedirects(response, self.PAGES_URLS['post_detail'])

        response = self.client.get(self.PAGES_URLS['post_edit'], follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))

    def test_urls_post_create_redirect_guest_on_login(self):
        """При запросе неавторизованным пользователем к страницам
        post_create, follow и попытке комментировать пост
        перенаправляет на страницу авторизации.
        """
        PAGES_AND_REDIRECTS_FOR_GUEST = {
            self.PAGES_URLS['post_create']: '/auth/login/?next=/create/',
            self.PAGES_URLS['follow_index']: '/auth/login/?next=/follow/',
            self.PAGES_URLS['add_comment']:
                f'/auth/login/?next=/posts/{self.post.id}/comment/',
        }

        for address, redirect in PAGES_AND_REDIRECTS_FOR_GUEST.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(
                    response, redirect)

    def test_urls_post_create_redirect_authorized_on_pfofile(self):
        """При запросе авторизованным пользователем страницы post_create,
        после заполнения формы перенаправляет на страницу профиля.
        """

        form_data = {
            'text': 'Текст',
            'group': self.group.id
        }

        response = self.authorized_client_1.post(
            self.PAGES_URLS['post_create'],
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, self.PAGES_URLS['profile'])

    def test_urls_add_comments_avalible_only_for_authorized(self):
        """Комментирование поста доступно только авторизованному
        пользователю.
        """

        response = self.authorized_client_2.get(
            self.PAGES_URLS['add_comment'],
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
