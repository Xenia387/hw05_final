from django.db import models

from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()
ADMIN_NUMBER_OF_CHARACTERS = 15


class Group(models.Model):
    title = models.CharField(
        help_text='Название сообщества не должно быть длиннее 200 символов',
        max_length=200,
        verbose_name='Название группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес группы'
    )
    description = models.TextField(
        help_text='Добавьте описание сообщества.',
        verbose_name='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        help_text='Текст не должен быть длиннее 700 символов',
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:ADMIN_NUMBER_OF_CHARACTERS]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        help_text='Текст не должен быть длиннее 300 символов',
        verbose_name='Текст'
    )

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписка',
    )
