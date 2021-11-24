from django.test import TestCase
from ..models import Follow, User
from django.urls import reverse
from .fixtures import UsersCreate, ObjectsCreate


TEXT = 'текст поста'


class TestFollows(TestCase):

    def setUp(self):

        self.post_author = UsersCreate.author_create()
        self.USER = UsersCreate.user_create()
        self.GUEST = UsersCreate.guest_client_create()
        self.AUTHOR = UsersCreate.authorized_author_client_create(
            self.post_author
        )
        self.AUTHORIZED_USER = UsersCreate.authorized_client_create(self.USER)
        self.GROUP = ObjectsCreate.group_create()
        self.POST = ObjectsCreate.post_create(
            self.GROUP, self.post_author, TEXT
        )
        self.PROFILE_FOLLOW = reverse(
            'posts:profile_follow', kwargs={
                'username': self.post_author.username
            }
        )
        self.PROFILE_UNFOLLOW = reverse(
            'posts:profile_unfollow', kwargs={
                'username': self.post_author.username
            }
        )
        self.FOLLOW_INDEX = reverse('posts:follow_index')

    def test_an_authorized_user_can_subscribe_to_other_users(self):
        "...and remove them from subscriptions"
        follow = Follow.objects.filter(user=self.USER, author=self.post_author)

        self.AUTHORIZED_USER.get(self.PROFILE_FOLLOW)
        self.assertTrue(follow.exists())

        self.AUTHORIZED_USER.get(self.PROFILE_UNFOLLOW)
        self.assertFalse(follow.exists())

        self.GUEST.get(self.PROFILE_FOLLOW)
        self.assertFalse(follow.exists())

    def test_a_new_post_appears_in_the_feed_of_subscribers(self):
        "...and does not appear in the feed of those who are not subscribed"
        unfollowed = User.objects.create(username='unfollowed')
        unfollowed_user = UsersCreate.authorized_client_create(unfollowed)

        self.AUTHORIZED_USER.get(self.PROFILE_FOLLOW)
        response = self.AUTHORIZED_USER.get(self.FOLLOW_INDEX)
        follower_content = response.context['page_obj']

        self.assertEqual(follower_content[0].text, TEXT)
        self.assertEqual(follower_content[0].group, self.GROUP)
        self.assertEqual(follower_content[0].author, self.post_author)

        response = unfollowed_user.get(self.FOLLOW_INDEX)
        unfollower_content = response.context['page_obj']
        self.assertNotIn(follower_content[0], unfollower_content)
