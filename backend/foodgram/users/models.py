from django.contrib.auth.models import AbstractUser
from django.db import models

ADMIN = 'admin'
USER = 'user'


class User(AbstractUser):
    # Кастомная модель пользователя
    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        'Юзернейм пользователя',
        max_length=254,
        unique=True,
        blank=True,
        null=False
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=254,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=254,
        blank=False,
        null=False,
    )
    password = models.CharField(
        'Пароль',
        max_length=254,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    role = models.CharField(
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
