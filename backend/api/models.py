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


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
    )
    name = models.TextField('Название', max_length=256)
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)
    text = models.TextField('Описание', max_length=1000)
    сooking_time = models.IntegerField('Время приготовления в минутах')
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


# class RecipesTag(models.Model):
#     recipes = models.ForeignKey(
#         Recipes,
#         on_delete=models.CASCADE,
#         related_name='recipes',
#     )
#     tag = models.ForeignKey(
#         Tags,
#         on_delete=models.CASCADE,
#         related_name='tag',
#     )
#
#     def __str__(self):
#         return self.name

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['recipes', 'tag'],
    #             name='unique_follow'
    #         )
    #     ]


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


class Ingredients(models.Model):
    name = models.TextField('Название', max_length=256)
    measurement_unit = models.TextField('Единица измерения', max_length=16)
    amount = models.IntegerField('Количество')


class IngredientsRecipes(models.Model):
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipes', 'ingredients'],
                name='unique_follow'
            )
        ]
