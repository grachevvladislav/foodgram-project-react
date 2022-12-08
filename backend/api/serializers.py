from rest_framework import serializers

from users.serializers import UserSerializer
from .models import (
    Tag, Recipe, Ingredient, IngredientAmount, Favourites, Shopping_cart
)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'сooking_time')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(read_only=True, many=True)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'сooking_time'
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request', None).user
        if user.is_authenticated:
            return Favourites.objects.filter(
                user=user, recipes=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request', None).user
        if user.is_authenticated:
            return Shopping_cart.objects.filter(
                user=user, recipes=recipe
            ).exists()
        return False
