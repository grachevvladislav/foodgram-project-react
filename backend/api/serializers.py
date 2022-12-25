from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.conf import settings
from django.core.validators import MinValueValidator

from users.serializers import UserSerializer
from .fields import Base64ImageField
from .models import (Favourite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class TagsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=settings.TAG_NAME_MAX_LENGTH)
    color = serializers.CharField(max_length=settings.TAG_COLOR_MAX_LENGTH)
    slug = serializers.CharField(max_length=settings.TAG_SLUG_MAX_LENGTH)

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
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name',
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit',
        max_length=settings.INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1), ]
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
    image = Base64ImageField()
    name = serializers.CharField(max_length=settings.RECIPE_NAME_MAX_LENGTH)
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def add_ingredients(self, instance, ingredients_data):
        for ingredient_amount in ingredients_data:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_amount['ingredient']['id']
            )
            amount, _ = IngredientAmount.objects.get_or_create(
                ingredient=ingredient,
                amount=ingredient_amount['amount']
            )
            instance.ingredients.add(amount)
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        instance.tags.add(*tags_data)
        instance = self.add_ingredients(instance, ingredients_data)
        return instance

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            instance.ingredients.clear()
            instance = self.add_ingredients(instance, ingredients_data)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.add(*tags_data)
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
