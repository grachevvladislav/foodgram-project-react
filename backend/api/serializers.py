from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
from django.shortcuts import get_object_or_404

from users.serializers import UserSerializer
from .models import (
    Tag, Recipe, Ingredient, IngredientAmount, Favourites, Shopping_cart
)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

    def to_internal_value(self, data):
        tag = get_object_or_404(Tag, id=data)
        return tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'сooking_time')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        ingredient = get_object_or_404(Ingredient, id=data['id'])
        ingredient_amount, status = IngredientAmount.objects.get_or_create(
            ingredient=ingredient, amount=data['amount']
        )
        print(data)
        print(ingredient_amount)
        return ingredient_amount

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            recipe.tags.add(tag)
        for ingredient in ingredients_data:
            recipe.ingredients.add(ingredient)
        return recipe



    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.text = validated_data.get('text', instance.text)
    #     instance.image = validated_data.get('image', instance.image)
    #     instance.сooking_time = validated_data.get(
    #         'сooking_time', instance.сooking_time
    #     )
    #     instance.author_id = self.context.get("request").user.id
    #     print(11111111111111111111111111111111111111)
    #     tags_data = validated_data.pop('tags')
    #     lst = []
    #     for tag_id in tags_data:
    #         current_tag = Tag.objects.get(id=tag_id)
    #         lst.append(current_tag)
    #     instance.tags.set(lst)
    #     instance.save()
    #     return instance

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
