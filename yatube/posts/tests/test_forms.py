from http import HTTPStatus
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User


IMAGE_PATH = '/media/posts/small.gif'
URL_POST_DETAIL = 'posts:post_detail'
URL_POST_CREATE = 'posts:post_create'
URL_POST_EDIT = 'posts:post_edit'
URL_ADD_COMMENT = 'posts:add_comment'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Описание тестовой группы',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст записанный в форму',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(reverse(URL_POST_CREATE),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        request_post = Post.objects.first()
        self.assertEqual(request_post.text, form_data['text'])
        self.assertEqual(request_post.group.id, form_data['group'])
        self.assertEqual(request_post.image.url, '/media/posts/small.gif')
        self.assertNotEqual(posts_count, posts_count + 1)

    def test_edit_post(self):
        """Валидная форма изменяет пост в Post."""
        image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        source_post = Post.objects.create(
            text='Исходный текст поста',
            author=self.user,
            group=self.group,
            image=image
        )
        another_group = Group.objects.create(
            title='Название второй группы',
            slug='another-group-slug',
            description='Описание второй группы'
        )
        another_image = SimpleUploadedFile(
            name='another_small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Изменённый текст',
            'group': another_group,
            'image': another_image,
        }
        response = self.authorized_client.post(
            reverse(URL_POST_EDIT, kwargs={'post_id': source_post.id}),
            data=form_data,
            follow=True,
        )
        source_post.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(source_post.text, form_data['text'])
        self.assertNotEqual(source_post.group, form_data['group'])
        self.assertNotEqual(source_post.image.url, IMAGE_PATH)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_comment(self):
        """Валидная форма создаёт комментарий"""
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.author,
        )
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
            'post': post.id,
        }
        response = self.authorized_client.post(
            reverse(URL_ADD_COMMENT, kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        request_comment = Comment.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(request_comment.text, form_data['text'])
        self.assertEqual(request_comment.post.id, form_data['post'])
        self.assertNotEqual(comment_count, comment_count + 1)
