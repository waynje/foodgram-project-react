from django.contrib.auth.models import (
    AbstractUser,
    Model
)
from django.db.models import (
    CharField,
    EmailField,
    ForeignKey,
    UniqueConstraint,
    CASCADE,
)

ADMIN = 'admin'
USER = 'user'


class User(AbstractUser):
    # Кастомная модель пользователя
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

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
    role = CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_user(self):
        return self.role == USER


class Subscription(Model):
    # Модель подписки
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
