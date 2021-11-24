import shutil
import tempfile

from django.contrib.auth import get_user_model

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Group, Post
from .fixtures import UsersCreate, ObjectsCreate


User = get_user_model()
TEXT = 'текст поста'
INDEX = reverse('posts:index')


class PagesUsesCorrectTemplates(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='Заголовок',
            slug='test_slug',
        )

    def setUp(self):

        self.post = Post.objects.create(
            author=User.objects.create(username='test_user'),
            text='проверка',
        )
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        response = self.authorized_client_author.get(
            reverse('posts:post_create')
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),

            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': 'test_slug'}),

            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': 'test_user'}),

            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),

            'posts/create_post.html':
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PagesHaveCorrectContexts(TestCase):

    def setUp(self):

        self.author = User.objects.create(
            username='test_name'
        )

        self.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug',
        )

        self.post = Post.objects.create(
            author=self.author,
            text='Текст, написанный для проверки',
            group=self.group
        )

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def post_exist_check(self, context):
        if 'page_obj' in context:
            posts = context['page_obj']
            post = posts[0]
        else:
            post = context['post']
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)

    def test_index_page_context(self):
        path = reverse('posts:index')
        response = self.authorized_client_author.get(path)
        context = response.context
        self.post_exist_check(context)

    def test_group_page_context(self):
        path = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.authorized_client_author.get(path)
        context = response.context
        self.post_exist_check(context)
        self.assertEqual(response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        path = reverse(
            'posts:profile', kwargs={'username': self.author.username}
        )
        response = self.authorized_client_author.get(path)
        context = response.context
        self.post_exist_check(context)
        self.assertEqual(response.context['author'], self.author)

    def test_detail_page_show_correct_context(self):
        path = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.authorized_client_author.get(path)
        context = response.context
        self.post_exist_check(context)

    def test_edit_page_show_correct_context(self):
        path = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        response = self.authorized_client_author.get(path)
        form = response.context.get('form')
        self.assertEqual(form.instance, self.post)

    def test_create_page_show_correct_context(self):
        path = reverse('posts:post_create')
        response = self.authorized_client_author.get(path)
        form = response.context.get('form')
        self.assertEqual(form.instance.text, '')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Group.objects.create(
            title='Заголовок',
            slug='test_slug',
        )

    def setUp(self):
        self.author = User.objects.create(username='test_user')
        self.group = Group.objects.get(slug='test_slug')

        for post_number in range(1, 14):
            self.post = Post.objects.create(
                author=self.author,
                text=('Этот пост, благодаря наставничеству ревьюера,'
                      'создаётся автоматически. '
                      f'И это пост номер {post_number}'),
                group=self.group
            )

    def test_for_contains_ten_and_three_records(self):
        paths_for_test_pages = {
            reverse('posts:index'): 10,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): 10,
            reverse('posts:profile', kwargs={
                'username': self.author.username
            }): 10,
            reverse('posts:index') + '?page=2': 3,
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}) + '?page=2': 3,
            reverse('posts:profile',
                    kwargs={'username': self.author.username}) + '?page=2': 3,
        }
        for keys, values in paths_for_test_pages.items():
            with self.subTest(keys=keys):
                response = self.client.get(keys)
                self.assertEqual(len(response.context['page_obj']), values)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PictureTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author = User.objects.create(
            username='test_name'
        )

        self.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        self.post = Post.objects.create(
            author=self.author,
            text='Текст, написанный для проверки',
            group=self.group,
            image=self.uploaded,
        )

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)

    def image_in_post_check(self, context):
        if 'page_obj' in context:
            posts = context['page_obj']
            post = posts[0]
        else:
            post = context['post']
        self.assertEqual(post.image, self.post.image)

    def test_the_picture_is_transmitted_in_page_context(self):
        paths = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ),
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ),
        ]
        for path in paths:
            response = self.authorized_client_author.get(path)
            context = response.context
            self.image_in_post_check(context)


class TestCache(TestCase):

    def setUp(self):
        self.post_author = UsersCreate.author_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create(
            self.post_author
        )
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.post_author, TEXT
        )

    def test_cache(self):
        response = self.AUTHOR.get(INDEX)
        image_of_page_BEFORE_post_delete = response.content
        post_to_delete = Post.objects.first()
        post_to_delete.delete()
        response = self.AUTHOR.get(INDEX)
        image_of_page_AFTER_post_delete = response.content
        self.assertEqual(
            image_of_page_BEFORE_post_delete, image_of_page_AFTER_post_delete
        )
