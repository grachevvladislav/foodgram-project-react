from django.contrib import admin

from .models import (
    Recipe, Tag, Shopping_cart, Favourites,
    IngredientAmount, Ingredient
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingredient', 'amount']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']


@admin.register(Shopping_cart, Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipes']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'text', 'author', 'сooking_time']
    ordering = ['name', 'author', 'сooking_time']
    filter_horizontal = ['tags', 'ingredients']
