import time
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import FileField, ImageFieldFile
from django.core.cache import cache

from ..models import Group, Post, User
from ..constants import NUMBER_OF_POSTS_ON_PAGE, NUMBER_OF_TEST_POSTS


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorized_client_1 = Client()
        cls.user_1 = User.objects.create_user(username='TestUser1')
        cls.authorized_client_1.force_login(cls.user_1)

        cls.authorized_client_2 = Client()
        cls.user_2 = User.objects.create_user(username='TestUser2')
        cls.authorized_client_2.force_login(cls.user_2)

        cls.group_1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post_1 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост_1',
            group=cls.group_1,
            image=cls.uploaded
        )
        time.sleep(0.001)

        cls.post_2 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост_2',
            group=cls.group_1,
        )

        cls.image = ImageFieldFile(
            name='posts/small.gif',
            instance=cls.post_1,
            field=FileField(),
        )
        cls.PAGES_REVERSE = {
            'index': reverse(
                'posts:index'
            ),
            'group_list_1': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group_1.slug}
            ),
            'group_list_2': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group_2.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.user_1.username}
            ),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post_1.id}
            ),
            'post_create': reverse(
                'posts:post_create'
            ),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post_1.id}
            )
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()        
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):        
        cache.clear()
        
    def test_views_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            self.PAGES_REVERSE['index']: 'posts/index.html',
            self.PAGES_REVERSE['group_list_1']: 'posts/group_list.html',
            self.PAGES_REVERSE['profile']: 'posts/profile.html',
            self.PAGES_REVERSE['post_detail']: 'posts/post_detail.html',
            self.PAGES_REVERSE['post_create']: 'posts/create_post.html',
            self.PAGES_REVERSE['post_edit']: 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_index_group_list_profile_show_correct_context(self):
        """В контекст шаблонов index, group_list и profile входит
        список постов (page_obj). В контекст шаблонов post_detail,
        post_edit входит post.
        """

        PAGES = {
            self.PAGES_REVERSE['index'],
            self.PAGES_REVERSE['group_list_1'],
            self.PAGES_REVERSE['profile'],
            self.PAGES_REVERSE['post_detail'],
            self.PAGES_REVERSE['post_edit'],

        }

        for page in PAGES:

            response = self.authorized_client_1.get(page)
            context = response.context

            if 'page_obj' in context:
                post = response.context['page_obj'][1]

            else:
                post = response.context['post']

            post_atribute_and_expected = {
                post.id: self.post_1.id,
                post.author: self.post_1.author,
                post.text: self.post_1.text,
                post.group: self.post_1.group,
                post.image: self.image,
            }

            for atribute, expected in post_atribute_and_expected.items():
                with self.subTest(atribute=atribute):
                    self.assertEqual(atribute, expected)

    def test_views_group_list_page_show_correct_context(self):
        """В контекст шаблона group_list входит group."""

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['group_list_1']
        )
        group = response.context['group']
        self.assertEqual(group.id, self.group_1.id)

    def test_views_profile_page_show_correct_context(self):
        """В контекста шаблона profile входит author."""

        response = self.authorized_client_1.get(self.PAGES_REVERSE['profile'])
        author = response.context['author']
        self.assertEqual(author, self.post_1.author)

    def test_views_post_edit_page_show_correct_context(self):
        """В контекст шаблона post_edit входит форма редактирования поста
        и булева переменная is_edit.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_edit']
        )
        form_contents = {
            'text': self.post_1.text,
            'group': self.group_1,
        }

        for value, expected in form_contents.items():
            with self.subTest(value=value):
                form_content = getattr(
                    response.context.get('form').instance,
                    value
                )
                self.assertEqual(form_content, expected)

        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, True)

    def test_views_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом:
        форма создания поста.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_edit']
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_post_is_on_expected_pages(self):
        """При создании поста c указанной группой этот пост
        появляется на главной странице сайта, на странице
        выбранной группы, в профайле пользователя.
        """
        reverse_names = {
            self.PAGES_REVERSE['index'],
            self.PAGES_REVERSE['profile'],
            self.PAGES_REVERSE['group_list_1'],
        }

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                context = self.authorized_client_1.get(
                    reverse_name
                ).context['page_obj']
                self.assertEqual(Post.objects.latest('pub_date'), context[0])

    def test_views_post_is_not_on_unexpected_pages(self):
        """При создании поста c указанной группой этот пост
        не появляется странице другой группы.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['group_list_2']
        )
        context = response.context['page_obj']
        self.assertNotIn(self.post_1, context)

    def test_cache_index(self):
        """Проверкаработы кеша."""
        
        response = self.authorized_client_1.get(self.PAGES_REVERSE['index'])
        
        posts = response.content
        
        Post.objects.create(
            text='Пост для проверки кеша',
            author=self.user_1,
        )
        response_first = self.authorized_client_1.get(self.PAGES_REVERSE['index'])        
        first_posts = response_first.content
        
        self.assertEqual(first_posts, posts)

        cache.clear()

        response_second = self.authorized_client_1.get(self.PAGES_REVERSE['index'])      
        new_posts = response_second.content
        
        self.assertNotEqual(first_posts, new_posts)
        
    def test_authorized_follover(self):
        """Авторизованный пользователь может подписываться на других авторов
        и удалять их из подписок."""
        pass    
            
    def test_new_post_folloving(self):
        """Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан."""
        pass    

class PaginatorViewsTest(TestCase):
    """Проверка работы пагинатора."""

    def setUp(self):        
        cache.clear()
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestUser')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        posts = []
        for i in range(NUMBER_OF_TEST_POSTS):
            posts.append(
                Post(
                    author=cls.user,
                    text=f'Пост номер {i}',
                    id=i,
                    group=cls.group,
                )

            )

        Post.objects.bulk_create(posts)

        cls.reverse_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={'username': cls.user.username}),
        }

    def test_paginator_first_page(self):
        """"Первая страница содержит ожидаемое колличество записей."""

        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    NUMBER_OF_POSTS_ON_PAGE
                )

    def test_paginator_second_page(self):
        """"Последняя страница содержит ожидаемое колличество записей."""

        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    NUMBER_OF_TEST_POSTS - NUMBER_OF_POSTS_ON_PAGE
                )

    
    
