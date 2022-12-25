from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.TextField('Название', max_length=200, unique=True)
    color = models.TextField(
        'Цвет', max_length=7, unique=True, default="#ffffff"
    )
    slug = models.TextField('Идентификатор', max_length=200, unique=True)

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
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
    )
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(0), ]
    )

    class Meta:
        ordering = ('ingredient',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

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
        related_name='recipes',
    )
    name = models.TextField('Название', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/')
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(1),
        ]
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(IngredientAmount)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favourite(models.Model):
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
                name='unique_recipe'
            )
        ]
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} {self.recipes.name}'


class ShoppingCart(models.Model):
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
                name='unique_shopping_cart'
            )
        ]
        ordering = ('user',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
