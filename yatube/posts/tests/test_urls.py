from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User

URL_ADD_COMMENT = 'posts:add_comment'
URL_INDEX = 'posts:index'
URL_FOLLOW_INDEX = 'posts:follow_index'
URL_GROUP_LIST = 'posts:group_list'
URL_PROFILE = 'posts:profile'
URL_PROFILE_FOLLOW = 'posts:profile_follow'
URL_PROFILE_UNFOLLOW = 'posts:profile_unfollow'
URL_POST_DETAIL = 'posts:post_detail'
URL_POST_CREATE = 'posts:post_create'
URL_POST_EDIT = 'posts:post_edit'
URL_UNEXISTING = '/unexisting_page/'
TEMPLATE_ADD_COMMENT = 'posts/add_comment.html'
TEMPLATE_INDEX = 'posts/index.html'
TEMPLATE_FOLLOW_INDEX = 'posts/follow.html'
TEMPLATE_GROUP_LIST = 'posts/group_list.html'
TEMPLATE_PROFILE = 'posts/profile.html'
TEMPLATE_POST_DETAIL = 'posts/post_detail.html'
TEMPLATE_POST_CREATE = 'posts/post_create.html'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()
        self.index_data = (
            reverse(URL_INDEX), TEMPLATE_INDEX, self.guest_client,
            HTTPStatus.OK
        )
        self.group_data = (
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug}),
            TEMPLATE_GROUP_LIST, self.guest_client, HTTPStatus.OK
        )
        self.profile_data = (
            reverse(URL_PROFILE, kwargs={'username': self.post.author}),
            TEMPLATE_PROFILE, self.guest_client, HTTPStatus.OK
        )
        self.post_detail_data = (
            reverse(URL_POST_DETAIL, kwargs={'post_id': self.post.id}),
            TEMPLATE_POST_DETAIL, self.guest_client, HTTPStatus.OK
        )
        self.post_create_data = (
            reverse(URL_POST_CREATE),
            TEMPLATE_POST_CREATE, self.authorized_client, HTTPStatus.OK
        )
        self.post_edit_data = (
            reverse(URL_POST_EDIT, kwargs={'post_id': self.post.id}),
            TEMPLATE_POST_CREATE, self.author_client, HTTPStatus.OK
        )
        self.unexisting_data = (
            URL_UNEXISTING, None, self.guest_client, HTTPStatus.NOT_FOUND
        )

    def test_pages_status(self):
        """Проверка доступа страниц"""
        pages = (
            self.index_data, self.group_data, self.profile_data,
            self.post_detail_data, self.post_create_data,
            self.post_edit_data, self.unexisting_data
        )
        for url, _, client, status_code in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_uses_template_any_client(self):
        """URL-адрес для всех пользователей использует соответствующий шаблон.
        """
        pages = (
            self.index_data, self.group_data, self.profile_data,
            self.post_detail_data, self.post_create_data,
            self.post_edit_data,
        )
        for url, template, client, _ in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertTemplateUsed(response, template)


class CommentURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower_author_comment = User.objects.create_user(
            username='follower'
        )
        cls.user = User.objects.create_user(
            username='following',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.follower_author_comment,
            post=cls.post,
            text='Текст комментария'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower_author_comment)
        self.author_client = Client()
        self.author_client.force_login(self.user)
        cache.clear()
        self.add_comment_data = (
            reverse(URL_POST_DETAIL, kwargs={'post_id': self.post.id}),
            TEMPLATE_ADD_COMMENT, self.authorized_client, HTTPStatus.OK
        )

    def test_access_url_authorized_client(self):
        """Страницы, доступные авторизованным пользователям"""
        pages = (
            self.add_comment_data,
        )
        for url, _, client, status_code in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_uses_template_auth_client(self):
        """URL-адрес добавления комментарий для авторизованных пользователей
        использует соответствующий шаблон.
        """
        pages = (self.add_comment_data,)
        for url, template, client, _ in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertTemplateUsed(response, template)


class FollowURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.following = User.objects.create_user(
            username='following',
        )

        cls.post = Post.objects.create(
            author=cls.following,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)
        self.author_client = Client()
        self.author_client.force_login(self.following)
        cache.clear()
        self.follow_index_data = (
            reverse(URL_FOLLOW_INDEX), TEMPLATE_FOLLOW_INDEX,
            self.author_client, HTTPStatus.OK
        )

    def test_access_url_authorized_client(self):
        """Страницы, доступные авторизованным пользователям"""
        pages = (self.follow_index_data,)
        for url, _, client, status_code in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_uses_template_auth_client(self):
        """URL-адрес для авторизованных пользователей использует
        соответствующий шаблон.
        """
        pages = (self.follow_index_data,)
        for url, template, client, _ in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertTemplateUsed(response, template)
