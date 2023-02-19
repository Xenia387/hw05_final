from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

URL_INDEX = 'posts:index'
URL_GROUP_LIST = 'posts:group_list'
URL_PROFILE = 'posts:profile'
URL_POST_DETAIL = 'posts:post_detail'
URL_POST_CREATE = 'posts:post_create'
URL_POST_EDIT = 'posts:post_edit'
URL_ADD_COMMENT = 'posts:add_comment'
TEMPLATE_INDEX = 'posts/index.html'
TEMPLATE_GROUP_LIST = 'posts/group_list.html'
TEMPLATE_PROFILE = 'posts/profile.html'
TEMPLATE_POST_DETAIL = 'posts/post_detail.html'
TEMPLATE_POST_CREATE = 'posts/post_create.html'


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user)
        cache.clear()

    def test_access_url_any_client(self):
        """Страницы, доступные всем пользователям"""
        ADDRESS = [
            reverse(URL_INDEX),
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(URL_PROFILE, kwargs={'username': self.post.author}),
            reverse(URL_POST_DETAIL, kwargs={'post_id': self.post.id}),
        ]
        for address in ADDRESS:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_url_author_post(self):
        """Страницы, доступные автору поста"""
        response = self.author_client.get(
            URL_POST_EDIT, kwargs={'post_id': self.post.id}
        )
        if self.author_client == self.user.username:
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_url_authorized_client(self):
        """Страницы, доступные авторизованным пользователям"""
        ADDRESS = [
            reverse(URL_POST_CREATE),
            reverse(URL_ADD_COMMENT, kwargs={'post_id': self.post.id}),
        ]
        for address in ADDRESS:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_uses_template_any_client(self):
        """URL-адрес для всех пользователей использует соответствующий шаблон.
        """
        template_url_names = {
            reverse(URL_INDEX):
                TEMPLATE_INDEX,
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug}):
                TEMPLATE_GROUP_LIST,
            reverse(URL_PROFILE, kwargs={'username': self.post.author}):
                TEMPLATE_PROFILE,
            reverse(URL_POST_DETAIL, kwargs={'post_id': self.post.id}):
                TEMPLATE_POST_DETAIL,
        }
        for address, template in template_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_uses_template_author_post(self):
        """URL-адрес для авторов постов использует соответствующий шаблон."""
        response = self.authorized_client.get(
            reverse(URL_POST_EDIT, kwargs={'post_id': self.post.id})
        )
        self.assertTemplateUsed(response, TEMPLATE_POST_CREATE)

    def test_uses_template_auth_client(self):
        """URL-адрес для авторизованных пользователей использует
        соответствующий шаблон.
        """
        response = self.authorized_client.get(reverse(URL_POST_CREATE))
        self.assertTemplateUsed(response, TEMPLATE_POST_CREATE)
