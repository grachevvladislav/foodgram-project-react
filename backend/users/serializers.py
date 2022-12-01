from rest_framework import serializers

from .mixins import UsernameMixins
from .models import User, Follow


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
        user = self.context.get('request', None).user  ## смотрящий
        return user == author


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()


class SubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')
        #read_only_fields = fields
