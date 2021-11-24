from .forms import PostForm, CommentForm
from .models import Follow, Post, Group, User
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings


def page_obj_gen(request, posts):
    paginator = Paginator(posts, settings.POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = Post.objects.all()
    page_obj = page_obj_gen(request, posts)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = f'Записи сообщества {group.title}'
    posts = group.posts.all()
    page_obj = page_obj_gen(request, posts)
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = page_obj_gen(request, posts)
    title = f'Профайл пользователя {author.get_full_name()}'
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
        else:
            following = False
    else:
        following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'title': title,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    title = f'Пост {post.text[:30]}'
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'form': form,
        'post': post,
        'title': title,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    else:
        print(form.errors)
    title = 'Новый пост'
    context = {
        'form': form,
        'is_edit': False,
        'title': title,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id=post_id)
    title = 'Редактирование поста'
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
        'title': title,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    else:
        print(form.errors)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    if Follow.objects.filter(user=request.user).exists():
        followings = Follow.objects.filter(
            user=request.user
        ).values_list('author')
        posts = Post.objects.filter(author_id__in=followings)
    else:
        posts = Post.objects.none()
    title = 'Посты избранных авторов'
    context = {
        'page_obj': posts,
        'title': title,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if Follow.objects.filter(user=request.user, author=author).exists():
        following = False
    elif user != author:
        Follow.objects.create(user=user, author=author)
        following = True
    else:
        following = True
    posts = author.posts.all()
    page_obj = page_obj_gen(request, posts)
    title = f'Профайл пользователя {author.get_full_name()}'
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.filter(
            user=user, author=author
        ).delete()
        following = False
    else:
        following = True
    posts = author.posts.all()
    page_obj = page_obj_gen(request, posts)
    title = f'Профайл пользователя {author.get_full_name()}'
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/profile.html', context)
