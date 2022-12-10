from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.TextField('Название', max_length=256, unique=True)
    color = models.TextField(
        'Цвет', max_length=7, unique=True, default="#ffffff"
    )
    slug = models.TextField('Идентификатор', max_length=256, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.TextField('Название', max_length=256)
    measurement_unit = models.TextField('Единица измерения', max_length=16)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Инградиент'
        verbose_name_plural = 'Инградиенты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    amount = models.IntegerField('Количество')

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'Количество инградиента'
        verbose_name_plural = 'Количество инградиентов'

    def __str__(self):
        return ' '.join([
            self.ingredient.name,
            str(self.amount),
            self.ingredient.measurement_unit
        ])


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
    )
    name = models.TextField('Название', max_length=256)
    image = models.ImageField('Картинка', upload_to='recipes/')
    text = models.TextField('Описание', max_length=1000)
    сooking_time = models.IntegerField('Время приготовления в минутах')
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(IngredientAmount)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favourites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipes', 'user'],
                name='unique_follow'
            )
        ]
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipes', 'user'],
                name='unique_follow'
            )
        ]
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
