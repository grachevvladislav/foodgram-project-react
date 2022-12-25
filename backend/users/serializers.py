from rest_framework import serializers
from django.conf import settings
from django.core.validators import MinValueValidator

from api.models import Recipe
from .mixins import UsernameMixins
from .models import Follow, User


class UserPostSerializer(serializers.ModelSerializer, UsernameMixins):
    username = serializers.CharField(max_length=settings.USERNAME_MAX_LENGTH)
    first_name = serializers.CharField(
        max_length=settings.FIRST_NAME_MAX_LENGTH
    )
    last_name = serializers.CharField(max_length=settings.LAST_NAME_MAX_LENGTH)
    password = serializers.CharField(max_length=settings.PASSWORD_MAX_LENGTH)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer, UsernameMixins):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password', 'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, author):
        user = self.context.get('request', None).user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=author).exists()
        return False


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=settings.RECIPE_NAME_MAX_LENGTH)
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class UserRecipeSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    email = serializers.EmailField(max_length=settings.EMAIL_MAX_LENGTH)
    username = serializers.CharField(max_length=settings.USERNAME_MAX_LENGTH)

    class Meta(UserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'password', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        recipes = Recipe.objects.filter(author=author)
        recipes_limit = self.context.get(
            'request', None
        ).query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeSubscribeSerializer(recipes, many=True).data


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField(max_length=settings.EMAIL_MAX_LENGTH)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()
