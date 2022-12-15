from rest_framework import serializers

from users.serializers import UserSerializer
from .fields import Base64ImageField
from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


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
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'сooking_time'
        )

    def add_tag_or_ingredient(self, instance, tags_data, ingredients_data):
        for item in tags_data:
            instance.tags.add(item)
        for item in ingredients_data:
            instance.ingredients.add(item)
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        instance = self.add_tag_or_ingredient(
            instance, tags_data, ingredients_data
        )
        return instance

    def update(self, instance, validated_data):
        instance = super().update(self, instance, validated_data)
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        instance.ingredients.clear()
        instance = self.add_tag_or_ingredient(
            instance, tags_data, ingredients_data
        )
        return instance

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favourite.objects.filter(
                user=user, recipes=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user, recipes=recipe
            ).exists()
        return False
