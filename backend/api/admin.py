from django.contrib import admin

from .models import (
    Recipe, Tag, Shopping_cart, Favourites,
    IngredientAmount, Ingredient
)


@admin.register(Tag, IngredientAmount, Ingredient)
class ApiAdmin(admin.ModelAdmin):
    pass


@admin.register(Shopping_cart, Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipes']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'author', 'сooking_time']
    ordering = ['name', 'author', 'сooking_time']
    filter_horizontal = ['tags', 'ingredients']
