from rest_framework import serializers

from .mixins import UsernameMixins
from .models import User, Follow
from api.models import Recipe


class UserPostSerializer(serializers.ModelSerializer, UsernameMixins):
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
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'сooking_time'
        )


class UserRecipeSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSubscribeSerializer(read_only=True, many=True)

    class Meta(UserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'password', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()
