from django.test import TestCase
from django.urls import reverse

from ..models import Comment
from .fixtures import UsersCreate, ObjectsCreate


TEXT = 'текст поста'


class TestComments(TestCase):

    def setUp(self):

        self.post_author = UsersCreate.author_create()
        self.GUEST = UsersCreate.guest_client_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create(
            self.post_author
        )
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.post_author, TEXT
        )
        self.COMMENT_ADD = reverse(
            'posts:add_comment', kwargs={'post_id': self.POST.id}
        )

    def test_unauthorized_user_cant_leave_a_comment(self):
        response = self.GUEST.get(self.COMMENT_ADD)
        self.assertEqual(response.status_code, 302)

    def test_the_comment_appears_on_the_post_after_successful_submission(self):
        comments_count = Comment.objects.count()
        form_data = {'text': 'Комментарий к посту'}
        self.AUTHOR.post(
            self.COMMENT_ADD,
            data=form_data,
            follow=True,
        )
        Comment.objects.count() == comments_count + 1
        latest_comment = Comment.objects.first()
        self.assertEqual(
            latest_comment.text, form_data['text']
        )
