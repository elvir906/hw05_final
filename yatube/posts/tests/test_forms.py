import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Post
from .fixtures import UsersCreate, ObjectsCreate

TEXT = 'Текст поста'


class TestFormActionAndResults(TestCase):
    def setUp(self):
        self.POST_AUTHOR = UsersCreate.author_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create(
            self.POST_AUTHOR
        )
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.POST_AUTHOR, TEXT
        )
        self.PROFILE = reverse(
            'posts:profile', kwargs={'username': self.POST_AUTHOR}
        )
        self.CREATE = reverse('posts:post_create')
        self.POST_EDIT = reverse(
            'posts:post_edit', kwargs={'post_id': self.POST.id}
        )

    def test_page_redirect_and_new_post_exists_after_post_create(self):
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'group': self.GROUP.id,
        }
        response = self.AUTHOR.post(
            self.CREATE,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.PROFILE)
        self.assertEqual(Post.objects.count(), post_count + 1)
        latest_post = Post.objects.first()
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertEqual(latest_post.author, self.POST_AUTHOR)
        self.assertEqual(latest_post.group, self.GROUP)

    def test_page_changes_when_edit(self):
        form_data = {
            'text': TEXT + ' изменение',
        }
        self.AUTHOR.post(
            self.POST_EDIT,
            data=form_data,
            follow=True,
        )
        changed_text = Post.objects.first()
        self.assertEqual(changed_text.text, form_data['text'])


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PictureTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.POST_AUTHOR = UsersCreate.author_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create(
            self.POST_AUTHOR
        )
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.POST_AUTHOR, TEXT
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
            content_type='image/gif',
        )
        self.post_count = Post.objects.count()

    def test_new_record_is_created_in_db(self):
        form_data = {
            'text': 'текст для проверки',
            'group': self.GROUP.id,
            'image': self.uploaded,
        }
        self.AUTHOR.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), self.post_count + 1)
        latest_post = Post.objects.first()
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertEqual(latest_post.author, self.POST_AUTHOR)
        self.assertEqual(latest_post.group.id, form_data['group'])
        img_name = latest_post.image.name.replace(
            latest_post.image.field.upload_to, ''
        )
        self.assertEqual(
            img_name,
            form_data['image'].name
        )
