from django.test import TestCase

from posts.models import ADMIN_NUMBER_OF_CHARACTERS, Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Проверка обзрезки поста в админ-зоне до 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_text = post.text[:ADMIN_NUMBER_OF_CHARACTERS]
        group = PostModelTest.group
        expected_title = group.title
        post_fields = (
            (post, expected_text),
            (group, expected_title),
        )
        for object, expected in post_fields:
            with self.subTest(object=object):
                self.assertEqual(expected, str(object))

    def test_verbose_name(self):
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Название сообщества не должно быть длиннее 200 символов',
            'description': 'Добавьте описание сообщества.',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )

        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст не должен быть длиннее 700 символов',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_post = User.objects.create_user(username='author_post')
        cls.author_comment = User.objects.yser(username='author_post')
        cls.post = Post.objects.create(
            author=cls.author_post,
            text='Проверка обзрезки поста в админ-зоне до 15 символов',
        )
        cls.comment = Comment.objects.create(
            author=cls.author_comment,
            post=cls.post,
            text='Текст комментария'
        )

        def test_verbose_name(self):
            comment = CommentModelTest.comment
            field_verboses = {
                'post': 'Пост, к которму относится комментарий',
                'author': 'Автор комментария',
                'text': 'Текст комментария',
            }
            for field, expected_value in field_verboses.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        comment._meta.get_field(field).verbose_name,
                        expected_value
                    )

        def test_help_text(self):
            """help_text в полях совпадает с ожидаемым."""
            comment = CommentModelTest.comment
            field_help_texts = {
                'post': 'Оставьте здесь свой комментарий',
                'text': 'Текст не должен быть длиннее 300 символов',
            }
            for field, expected_value in field_help_texts.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        comment._meta.get_field(field).help_text,
                        expected_value
                    )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.creat(
            user=cls.user,
            author=cls.author,
        )

        def test_verbose_name(self):
            follow = FollowModelTest.follow
            field_verboses = {
                'user': 'Подпички',
                'author': 'Подписка',
            }
            for field, expected_value in field_verboses.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        follow._meta.get_field(field).verbose_name,
                        expected_value
                    )

        def test_help_text(self):
            follow = FollowModelTest.follow
            field_help_texts = {
                'author': 'Вы можете подписаться на этого пользователя',
            }
            for field, expected_value in field_help_texts.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        follow._meta.get_field(field).help_text,
                        expected_value
                    )
