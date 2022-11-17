from django.db import models

from users.models import User


class Subscriptions(models.Model):
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
    )
    name = models.TextField(
        'Название',
        max_length=256
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    text = models.TextField(
        'Описание',
        max_length=1000
    )
    сooking_time = models.IntegerField(
        'Время приготовления в минутах',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name