from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    EmailField,
    ForeignKey,
    UniqueConstraint,
    CASCADE,
)


class User(AbstractUser):

    username = CharField(
        'Юзернейм пользователя',
        max_length=254,
        unique=True,
        blank=True,
        null=False
    )
    first_name = CharField(
        'Имя пользователя',
        max_length=254,
        blank=False,
        null=False,
    )
    last_name = CharField(
        'Фамилия пользователя',
        max_length=254,
        blank=False,
        null=False,
    )
    password = CharField(
        'Пароль',
        max_length=254,
        blank=False,
        null=False,
    )
    email = EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(Model):

    user = ForeignKey(
        'Пользователь',
        User,
        on_delete=CASCADE,
        related_name='follower',
    )
    author = ForeignKey(
        'Автор',
        User,
        on_delete=CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.usename} подписался на {self.author.username}.'
