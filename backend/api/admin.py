from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ['id', 'ingredient', 'amount']


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ['id', 'name', 'measurement_unit']


admin.site.register(Ingredient, IngredientAdmin)


@admin.register(ShoppingCart, Favourite)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipes']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'text', 'author', 'cooking_time']
    ordering = ['name', 'author', 'cooking_time']
    filter_horizontal = ['tags', 'ingredients']
