import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.db.models.fields.files import FileField, ImageFieldFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..constants import NUMBER_OF_POSTS_ON_PAGE, NUMBER_OF_TEST_POSTS
from ..models import Group, Post, User, Follow, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Проверка контекста страниц приложения Posts и
    соответствия URL адресов шаблонам. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorized_client_1 = Client()
        cls.user_1 = User.objects.create_user(username='TestUser1')
        cls.authorized_client_1.force_login(cls.user_1)

        cls.authorized_client_2 = Client()
        cls.user_2 = User.objects.create_user(username='TestUser2')
        cls.authorized_client_2.force_login(cls.user_1)

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

        cls.post_2 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост_2',
            group=cls.group_1,
        )

        cls.comment = Comment.objects.create(
            post=cls.post_1,
            author=cls.user_2,
            text='Тестовый комментарий'
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
            ),
            'add_comment': reverse(
                'posts:add_comment',
                kwargs={'post_id': cls.post_1.id}
            ),
            'follow_index': reverse(
                'posts:follow_index'
            ),
        }

    def post_atribute_and_expected(self, post):
        """Метод для проверки поста в контексте страниц."""

        post_atribute_and_expected = {
            post.id: self.post_1.id,
            post.author: self.post_1.author,
            post.text: self.post_1.text,
            post.group: self.post_1.group,
            post.image: self.image,
        }
        
        for atribute, expected in post_atribute_and_expected.items():
            self.assertEqual(
                atribute,
                expected,
            )
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_views_pages_uses_correct_template(self):
        """URL-адреса страниц приложения posts используют
        соответствующие шаблоны.
        """

        templates_pages_names = {
            self.PAGES_REVERSE['index']: 'posts/index.html',
            self.PAGES_REVERSE['group_list_1']: 'posts/group_list.html',
            self.PAGES_REVERSE['profile']: 'posts/profile.html',
            self.PAGES_REVERSE['post_detail']: 'posts/post_detail.html',
            self.PAGES_REVERSE['post_create']: 'posts/create_post.html',
            self.PAGES_REVERSE['post_edit']: 'posts/create_post.html',
            self.PAGES_REVERSE['follow_index']: 'posts/follow.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_index_context(self):
        """В контекст шаблона index входит page_obj
        и отображается картинка поста.
        """

        response = self.authorized_client_1.get(self.PAGES_REVERSE['index'])
        post = response.context['page_obj'][1]

        self.post_atribute_and_expected(post)        

    def test_views_group_list_context(self):
        """В контекст шаблона group_list входит page_obj и group.
        У поста отображается картинка.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['group_list_1']
        )

        post = response.context['page_obj'][1]
        group = response.context['group']

        self.post_atribute_and_expected(post)

        self.assertEqual(
            group.id,
            self.group_1.id,
            'несоответствие в контексте страницы group_list (group)'
        )

    def test_views_profile_context(self):
        """В контекст шаблона profile входит page_obj и author.
        У поста отображается картинка.
        """

        response = self.authorized_client_1.get(self.PAGES_REVERSE['profile'])

        post = response.context['page_obj'][1]
        author = response.context['author']

        self.post_atribute_and_expected(post)

        self.assertEqual(
            author,
            self.post_1.author,
            'несоответствие в контексте страницы profile (author)'
        )

    def test_views_post_detail_context(self):
        """В контекст шаблона post_detail входит post, form и comments,
        отображается картинка."""

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_detail']
        )

        post = response.context['post']
        comment = response.context['comments'][0]
        form = response.context.get('form')

        self.post_atribute_and_expected(post)

        self.assertEqual(
            comment.id,
            self.comment.id,
            'несоответствие в контексте страницы post_detail (comment)'
        )

        self.assertIsInstance(
            form.fields.get('text'),
            forms.fields.CharField,
            'несоответствие в контексте страницы post_detail (form)'
        )

    def test_views_post_edit_context(self):
        """В контекст шаблона post_edit входит post, form,
        булева переменная is_edit.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_edit']
        )

        post = response.context['post']
        form = response.context.get('form')
        is_edit = response.context['is_edit']

        self.post_atribute_and_expected(post)

        form_contents = {
            'text': self.post_1.text,
            'group': self.group_1,
        }

        for value, expected in form_contents.items():
            with self.subTest(value=value):
                form_content = getattr(
                    form.instance,
                    value
                )
                self.assertEqual(
                    form_content,
                    expected,
                    'несоответствие в контексте страницы post_edit (form)'
                )

        self.assertEqual(
            is_edit,
            True,
            'несоответствие в контексте страницы post_edit (is_edit)'
        )

    def test_views_post_create_context(self):
        """Шаблон post_create сформирован с правильным контекстом:
        форма создания поста.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_create']
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    'несоответствие в контексте страницы post_create (form)'
                )

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
                self.assertEqual(
                    self.post_2,
                    context[0],                    
                )

    def test_views_post_is_not_on_unexpected_pages(self):
        """При создании поста c указанной группой этот пост
        не появляется странице другой группы.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['group_list_2']
        )
        context = response.context['page_obj']
        self.assertNotIn(
            self.post_1,
            context,
            'Пост появился на странице группы, в которую он не входит'
        )

    def test_cache_index(self):
        """Проверка работы кеша на странице index."""

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['index']
        )
        posts = response.content

        Post.objects.create(
            text='Пост для проверки кеша',
            author=self.user_1,
        )
        response_again = self.authorized_client_1.get(
            self.PAGES_REVERSE['index']
        )
        update_posts = response_again.content
        self.assertEqual(
            update_posts,
            posts,
            'Кеш не работает, новый пост сразу появляется на странице'
        )
        cache.clear()
        response_again_2 = self.authorized_client_1.get(
            self.PAGES_REVERSE['index']
        )
        update_posts_2 = response_again_2.content
        self.assertNotEqual(
            posts,
            update_posts_2,
            'Кеш не работает, новый пост не появляется на странице'
        )


class FollowTests(TestCase):
    """Проверка функций подписки/отписки. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorized_author = Client()
        cls.author = User.objects.create_user(username='Author')
        cls.authorized_author.force_login(cls.author)

        cls.authorized_follower = Client()
        cls.follower = User.objects.create_user(username='Follower')
        cls.authorized_follower.force_login(cls.follower)

        cls.authorized_not_follower = Client()
        cls.not_follower = User.objects.create_user(username='Not_follower')
        cls.authorized_not_follower.force_login(cls.not_follower)

        cls.post_1 = Post.objects.create(
            author=cls.author,
            text='Тестовый пост_1',
        )
        cls.comment = Comment.objects.create(
            post=cls.post_1,
            author=cls.follower,
            text='Тестовый комментарий'
        )

        cls.PAGES_REVERSE = {
            'follow_index': reverse(
                'posts:follow_index'
            ),
            'profile_follow': reverse(
                'posts:profile_follow',
                kwargs={'username': cls.author.username}
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': cls.author.username}
            ),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_authorized_can_follow(self):
        """Авторизованный пользователь может подписываться
        на других авторов.
        """

        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists(),
        ) 

        response = self.authorized_follower.get(
            self.PAGES_REVERSE['profile_follow'],
            follow=True
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
        )

        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.author
            ).exists(),            
        )
                
    def test_authorized_can_unfollow(self):
        """Авторизованный пользователь может удалять
        авторов из подписок.
        """

        follow = Follow.objects.create(user=self.follower, author=self.author)
        follow.save()        
        
        self.assertTrue(
            Follow.objects.filter(
                user=self.follower,
                author=self.author,                
            ).exists()            
        )

        response = self.authorized_follower.get(
            self.PAGES_REVERSE['profile_unfollow'],
            follow=True
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
        )

        self.assertFalse(
            Follow.objects.filter(
                user=self.follower,
                author=self.author,
            ).exists()
        )

    def test_new_post_follover(self):
        """Новая запись автора пользователя появляется
        в ленте его подписчиков.
        """

        Follow.objects.create(user=self.follower, author=self.author)
        
        follow_index_context = set(
            self.authorized_follower.get(
                self.PAGES_REVERSE['follow_index']
            ).context['page_obj'].object_list
        )
        new_post = Post.objects.create(
            author=self.author,
            text='Пост для проверки ленты подписок',
        )
        new_post.save()

        follow_index_context_new = set(
            self.authorized_follower.get(
                self.PAGES_REVERSE['follow_index']
            ).context['page_obj'].object_list
        )

        self.assertEqual(
            new_post,
            list(
                follow_index_context_new.difference(
                    follow_index_context
                )
            )[0],
        )

    def test_new_post_folloving(self):
        """Новая запись автора не появляется в ленте тех,
        кто на него не подписан.
        """

        self.assertFalse(
            Follow.objects.filter(
                user=self.not_follower,
                author=self.author
            ).exists()
        )

        follow_index_context = set(
            self.authorized_not_follower.get(
                self.PAGES_REVERSE['follow_index']
            ).context['page_obj'].object_list
        )

        new_post = Post.objects.create(
            author=self.author,
            text='Пост для проверки ленты подписок',
        )
        new_post.save()

        follow_index_context_new = set(
            self.authorized_not_follower.get(
                self.PAGES_REVERSE['follow_index']
            ).context['page_obj'].object_list
        )
        
        self.assertEqual(
            len(
                follow_index_context_new.difference(
                    follow_index_context
                )
            ), 0,
        )


class PaginatorViewsTest(TestCase):
    """Проверка работы пагинатора."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
                    NUMBER_OF_POSTS_ON_PAGE,
                )

    def test_paginator_second_page(self):
        """"Последняя страница содержит ожидаемое колличество записей."""

        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    NUMBER_OF_TEST_POSTS - NUMBER_OF_POSTS_ON_PAGE,
                )
