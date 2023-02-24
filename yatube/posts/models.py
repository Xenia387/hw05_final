from django.db import models

from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()
ADMIN_NUMBER_OF_CHARACTERS = 15
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class Group(models.Model):
    verbose_name = 'Группа'
    verbose_name_plural = 'Группы'
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
    verbose_name = 'Пост'
    verbose_name_plural = 'Посты'
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
        ordering = ('-created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:ADMIN_NUMBER_OF_CHARACTERS]


class Comment(CreatedModel):
    verbose_name = 'Комментарий'
    verbose_name_plural = 'Комментарии'
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, которому относится пост',
        help_text='Оставьте здесь свой комментарий',
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        help_text='Текст не должен быть длиннее 300 символов',
        verbose_name='Текст'
    )

    class Meta:
        ordering = ('-created',)


class Follow(models.Model):
    verbose_name = ''
    verbose_name_plural = ''
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписка',
        help_text='Вы можете подписаться на этого пользователя',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_user_author')
        ]
