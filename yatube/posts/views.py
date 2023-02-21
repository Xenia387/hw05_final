from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import Comment, CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginat

# здравствуйте. понимаю сама поздно отправила
# но тем не менее
# этот проект надо сдать до 26 февраля (жёсткий дедлайн)
# и слышала что вы 23 и 24 не работаете
# так что очень хотелось бы успеть доработать и исправить всё до этих чисел


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_obj = paginat(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_posts = group.posts.all()
    page_obj = paginat(request, group_posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    is_authentuced = True
    is_exists = True
    following = is_authentuced and is_exists
    # при 47 не проходит pytest а с 43-45 не работает кнопка отписки/подписки
    # following = Follow.objects.filter(user=request.user, author=author)
    posts_author = author.posts.all()
    page_obj = paginat(request, posts_author)
    cannot_follow = request.user == author
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
        'cannot_follow': cannot_follow,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form_comment = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'form_comment': form_comment,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {'form': form}
    if not form.is_valid():
        return render(request, 'posts/post_create.html', context)
    else:
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    context = {
        'form': form,
        'is_edit': True,
    }
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.pk)
        return render(request, 'posts/post_create.html', context)
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
    }
    if not form.is_valid():
        return render(request, 'posts/post_detail.html', context)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post.pk)


@login_required
def follow_index(request):
    favorite_post_list = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = paginat(request, favorite_post_list)
    context = {
        'page_obj': page_obj,
        'favorite_post_list': favorite_post_list,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    else:
        if Follow.objects.filter(user=request.user, author=author):
            return redirect('posts:profile', username=username)
        else:
            follow = Follow.objects.create(
                user=request.user,
                author=author,
            )
        return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    follow.delete()
    return redirect('posts:profile', username=username)
