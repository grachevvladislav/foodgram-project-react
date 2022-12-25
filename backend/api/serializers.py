from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.conf import settings

from users.serializers import UserSerializer
from .fields import Base64ImageField
from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

    def to_internal_value(self, data):
        """
        При создании рецепта возвращает тег по его id.
        """
        return get_object_or_404(Tag, id=data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        """
        При создании рецепта создает ингредиент-количества по id ингредиента
        и его количеству. Возвращает объект IngredientAmount.
        """
        ingredient = get_object_or_404(Ingredient, id=data['id'])
        ingredient_amount, status = IngredientAmount.objects.get_or_create(
            ingredient=ingredient, amount=data['amount']
        )
        return ingredient_amount


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    name = serializers.CharField(max_length=settings.RECIPE_NAME_MAX_LENGTH)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def add_tag_or_ingredient(self, instance, data, field):
        exec(f'instance.{field}.clear()')
        for item in data:
            exec(f'instance.{field}.add({item.id})')
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)

        instance = self.add_tag_or_ingredient(
            instance, ingredients_data, 'ingredients'
        )
        instance = self.add_tag_or_ingredient(
            instance, tags_data, 'tags'
        )
        return instance

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            data = validated_data.pop('ingredients')
            instance = self.add_tag_or_ingredient(
                instance, data, 'ingredients'
            )
        if 'tags' in validated_data:
            data = validated_data.pop('tags')
            instance = self.add_tag_or_ingredient(instance, data, 'tags')
        instance = super().update(instance, validated_data)
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
