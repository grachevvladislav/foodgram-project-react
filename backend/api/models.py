from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from users.models import User
from .validators import slug_validator


class Tag(models.Model):
    name = models.TextField(
        'Название',
        max_length=settings.TAG_NAME_MAX_LENGTH,
        unique=True
    )
    color = models.TextField(
        'Цвет',
        max_length=settings.TAG_COLOR_MAX_LENGTH,
        unique=True,
        default="#ffffff"
    )
    slug = models.TextField(
        'Идентификатор',
        max_length=settings.TAG_SLUG_MAX_LENGTH,
        unique=True,
        validators=[slug_validator]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.TextField(
        'Название',
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = models.TextField(
        'Единица измерения',
        max_length=settings.INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

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
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[
            MinValueValidator(1)
        ]
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
    name = models.TextField(
        'Название',
        max_length=settings.RECIPE_NAME_MAX_LENGTH
    )
    image = models.ImageField('Картинка', upload_to='recipes/')
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(1)
        ]
    )
    tags = models.ManyToManyField(Tag)
    ingredients = models.ManyToManyField(IngredientAmount)

    class Meta:
        ordering = ('-id',)
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
