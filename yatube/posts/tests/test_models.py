from django.test import TestCase
from django.core.cache import cache

from ..models import Group, Post, User
from ..constants import MAX_LENGHT_OF_RETURN_TEXT


class PostModelTest(TestCase):
    """Проверка модели Post."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):        
        cache.clear()
        
    def test_models_have_correct_object_names(self):
        """У моделей корректно работает __str__."""

        expected_str = {
            self.post: PostModelTest.post.text[:MAX_LENGHT_OF_RETURN_TEXT],
            self.group: PostModelTest.group.title,
        }

        for model, expected_value in expected_str.items():
            with self.subTest(model=model):
                self.assertEqual(expected_value, str(model))
