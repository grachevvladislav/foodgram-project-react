from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, CreateModelMixin

from .tokens import JWTAccessToken
from .models import User
from .serializers import (
    LoginSerializer, MeUserSerializer, UserSerializer, PasswordSerializer
)


WRONG_DATA = 'Неправильный email или пароль!'
WRONG_PASSWORD = 'Неправильный пароль!'


class UsersViewSet(ListModelMixin, CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    lookup_field = 'id'


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.data['email'])
    if check_password(serializer.data['password'], user.password):
        token = JWTAccessToken.for_user(user)
        return JsonResponse(
            {"auth_token": str(token)},
            status=status.HTTP_200_OK
        )
    raise ValidationError(WRONG_DATA)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(
        MeUserSerializer(request.user).data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_password(request):
    serializer = PasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if check_password(
        serializer.data['current_password'],
        request.user.password
    ):
        request.user.set_password(serializer.data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    raise ValidationError(WRONG_PASSWORD)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def del_token_view(request):
    token = JWTAccessToken(request.headers.get('Authorization').split(' ', 1)[1])
    token.blacklist()
    print(request.headers)
    return Response(status=status.HTTP_204_NO_CONTENT)
