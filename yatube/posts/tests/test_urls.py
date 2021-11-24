from django.contrib.auth import get_user_model

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )

        self.post = Post.objects.create(
            author=User.objects.create(username='test_user'),
            text='проверка',
        )

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.post.author)

    def test_urls_for_all_users(self):
        urls_and_response_statuses = {
            reverse('posts:index'): 200,
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }): 200,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): 200,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): 200,
            '/unexisting_page/': 404,
        }

        for urls, statuses in urls_and_response_statuses.items():
            with self.subTest(urls=urls):
                response = self.client.get(urls)
                self.assertEqual(response.status_code, statuses)

    def test_important_urls(self):
        responses_and_response_statuses = {
            self.guest_client.get(reverse('posts:post_create')): 302,
            self.guest_client.get(reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id})
            ): 302,
            self.authorized_client_author.get(reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id})
            ): 200,
        }

        for responses, statuses in responses_and_response_statuses.items():
            with self.subTest(responses=responses):
                response = responses
                self.assertEqual(response.status_code, statuses)

    def test_templates(self):
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile',
                    kwargs={
                        'username': self.user.username
                    }): 'posts/profile.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)
