from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from .validators import username_validator

SELF_FOLLOW = 'Нельзя подписаться на самого себя!'


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.FIRST_NAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LAST_NAME_MAX_LENGTH,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def clean(self):
        if self.user == self.author:
            raise ValidationError(SELF_FOLLOW)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
