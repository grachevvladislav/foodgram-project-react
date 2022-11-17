from rest_framework import serializers

from users.mixins import UsernameMixins
from users.models import User


class UserSerializer(serializers.ModelSerializer, UsernameMixins):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)
        #optional_fields = ('first_name', 'last_name', 'bio', 'role')


class MeUserSerializer(UserSerializer, UsernameMixins):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
