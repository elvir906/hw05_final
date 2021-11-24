from django.contrib.auth import get_user_model
from django.test import Client
from ..models import Group, Post


User = get_user_model()


class UsersCreate():
    def guest_client_create():
        guest = Client()
        return guest

    def author_create():
        author = User.objects.create(username='post_author')
        return author

    def authorized_author_client_create(author):
        authorized_author = Client()
        authorized_author.force_login(author)
        return authorized_author

    def user_create():
        user = User.objects.create(username='user')
        return user

    def authorized_client_create(user):
        authorized_user = Client()
        authorized_user.force_login(user)
        return authorized_user


class ObjectsCreate():
    def post_create(group, author, text):
        post = Post.objects.create(
            text=text,
            group=group,
            author=author
        )
        return post

    def group_create():
        group = Group.objects.create(
            slug='test_slug',
            title='group_title'
        )
        return group
