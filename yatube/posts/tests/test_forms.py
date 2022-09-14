import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import FileField, ImageFieldFile
from django.core.cache import cache

from ..forms import PostForm
from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorized_client = Client()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client.force_login(cls.user)

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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group_1,
        )
        cls.form = PostForm()

    def setUp(self):        
        cache.clear()
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_form_create_post(self):
        """При отправке валидной формы со страницы create_post
        создаётся новая запись в базе данных.
        """

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Новая запись',
            'group': self.group_1.id,
            'image': uploaded,
        }

        posts_id = list(Post.objects.values_list('id', flat=True))

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        added_post = Post.objects.exclude(id__in=posts_id)

        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )

        image = ImageFieldFile(
            name='posts/small.gif',
            instance=added_post,
            field=FileField(),
        )

        self.assertEqual(len(added_post), 1)
        self.assertEqual(added_post[0].group.id, form_data['group'])
        self.assertEqual(added_post[0].text, form_data['text'])
        self.assertEqual(added_post[0].image, image)

    def test_form_edit_post(self):
        """при отправке валидной формы со страницы post_edit
        происходит изменение поста с post_id в базе данных.
        """

        posts_count = Post.objects.count()

        form_data = {
            'text': 'Обновлённая запись поста',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                author=self.user,
                text=form_data['text'],
                group=self.group_2,
            ).exists()
        )
