from django.test import TestCase

from posts.models import ADMIN_NUMBER_OF_CHARACTERS, Group, Post, User


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
        tuple = (
            (post, expected_text),
            (group, expected_title),
        )
        for object, expected in tuple:
            with self.subTest(object=object):
                self.assertEqual(expected, str(object))

    def test_1(self):
        post = PostModelTest.post
        expected_object_text = post.text[:ADMIN_NUMBER_OF_CHARACTERS]
        self.assertEqual(expected_object_text, str(post))
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

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
                    group._meta.get_field(field).verbose_name, expected_value)

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
                    post._meta.get_field(field).verbose_name, expected_value)

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
                    group._meta.get_field(field).help_text, expected_value)

        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст не должен быть длиннее 700 символов',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
