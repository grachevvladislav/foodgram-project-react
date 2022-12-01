from django.contrib import admin

from .models import (
    Recipe, Tag, Shopping_cart, Favourites,
    IngredientsRecipes, Ingredients
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'author', 'сooking_time']
    ordering = ['name', 'author', 'сooking_time']
    filter_horizontal = ['tags']

