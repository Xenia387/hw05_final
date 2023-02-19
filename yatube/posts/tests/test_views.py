from django.core.cache import cache
from django.test import Client, TestCase, SimpleUploadedFile
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User
from posts.utils import POSTS_NUMBER

LIST_OF_TEST_POSTS = 13
URL_INDEX = 'posts:index'
URL_GROUP_LIST = 'posts:group_list'
URL_PROFILE = 'posts:profile'
URL_POST_DETAIL = 'posts:post_detail'
URL_POST_CREATE = 'posts:post_create'
URL_POST_EDIT = 'posts:post_edit'
URL_ADD_COMMENT = 'posts:add_comment'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=cls.image,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user)
        cache.clear()

    def test_index_correct_context(self):
        """Шаблон index сорфмирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(URL_INDEX))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, self.user.username)
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.image, 'posts/image.gif')

    def test_grouplist_correct_context(self):
        """Шаблон group_list сорфмирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, self.user.username)
        self.assertEqual(first_object.group.title, self.group.title)

    def test_profile_correct_context(self):
        """Шаблон profile сорфмирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(URL_PROFILE, kwargs={'username': self.post.author})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.author.username, self.user.username)
        self.assertEqual(first_object.group.title, self.group.title)

    def test_postdetail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(URL_POST_DETAIL, kwargs={'post_id': self.post.id}))
        post_text_0 = {
            response.context.get('post').text: 'Текст поста',
            response.context.get('post').group: 'Тестовая группа',
        }
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_editpost_correct_context(self):
        """Шаблон edit_post сорфмирован с правильным контекстом"""
        response = (self.authorized_client.get(
            reverse(URL_POST_EDIT, kwargs={'post_id': self.post.id})
        ))
        form_instance = response.context['form']
        self.assertIsInstance(form_instance, PostForm)

    def test_postcreate_correct_context(self):
        """Шаблон post_create сорфмирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(URL_POST_CREATE)
        )
        form_instance = response.context['form']
        self.assertIsInstance(form_instance, PostForm)

    def test_create_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Созданный пост',
            author=self.user,
            group=self.group,
            image=self.image
        )
        response_index = self.authorized_client.get(
            reverse(URL_INDEX)
        )
        response_group = self.authorized_client.get(
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug})
        )
        response_profile = self.authorized_client.get(
            reverse(URL_PROFILE, kwargs={'username': self.user.username})
        )
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, 'поста нет на главной')
        self.assertIn(post, group, 'поста нет в профиле')
        self.assertIn(post, profile, 'поста нет в группе')


class CommentViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_author_post = User.objects.create_user(username='auth2')
        cls.user_author_comment = User.objects.create_user(username='auth3')
        cls.post = Post.objects.create(
            author=cls.user_author_post,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_post_client = Client()
        self.author_post_client.force_login(self.user_author_post)
        self.author_comment_client = Client()
        self.author_comment_client.force_login(self.user_author_comment)

    def test_created_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        comment = Comment.objects.create(
            text='Созданный комментарий',
            author=self.user_author_comment,
            post=self.post,
        )
        response_post_detail = self.guest_client.get(
            reverse(URL_POST_DETAIL, kwargs={'post_id': self.post.id})
        )
        post_detail = response_post_detail.context
        self.assertIn(
            comment.id, post_detail, 'комментария нет на странице поста'
        )


class PaginatorViewsTest(TestCase):
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
            group=cls.group,
            text='Тестовый пост',
        )
        cls.empty_list = []
        for i in range((LIST_OF_TEST_POSTS - 1)):
            cls.empty_list.append(
                Post(
                    author=cls.user,
                    group=cls.group,
                    text=f'Текст тестового поста номер {i}'
                )
            )
        Post.objects.bulk_create(cls.empty_list)

    def test_first_page_contains_ten_posts(self):
        pages = [
            reverse(URL_INDEX),
            reverse(URL_PROFILE, kwargs={'username': self.post.author}),
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug}),
        ]
        for i in pages:
            response = self.client.get(i)
            self.assertEqual(len(response.context['page_obj']), POSTS_NUMBER)

    def test_second_page_contains_three_posts(self):
        pages = [
            reverse(URL_INDEX),
            reverse(URL_PROFILE, kwargs={'username': self.post.author}),
            reverse(URL_GROUP_LIST, kwargs={'slug': self.group.slug}),
        ]
        for i in pages:
            response = self.client.get(i + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                (LIST_OF_TEST_POSTS - POSTS_NUMBER)
            )
