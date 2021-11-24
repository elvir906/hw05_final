from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, который написал автор',
        )

    def test_post_model_have_correct_object_names(self):
        post = PostModelTest.post
        self.assertEqual(post.__str__(), post.text[:15])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_post_model_have_correct_object_names(self):
        group = GroupModelTest.group
        group_str = group.__str__()
        self.assertEqual(group_str, group.title)
