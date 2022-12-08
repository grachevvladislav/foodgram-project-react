from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as ValidationError_db
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin
)
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from .tokens import JWTAccessToken
from .models import User, Follow
from .serializers import (
    LoginSerializer, UserSerializer, PasswordSerializer,
    UserPostSerializer, UserRecipeSerializer
)


WRONG_DATA = 'Неправильный email или пароль!'
WRONG_PASSWORD = 'Неправильный пароль!'
UNSUBSCRIBE_ERROR = 'Вы не были подписаны!'


class UsersViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.validated_data['password'] = make_password(
            serializer.validated_data['password']
        )
        serializer.save()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserPostSerializer
        return UserSerializer


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
        UserSerializer(request.user, context={'request': request}).data,
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
    token = JWTAccessToken(request.headers.get(
        'Authorization'
    ).split(' ', 1)[1])
    token.blacklist()
    print(request.headers)
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_follows(request):
    user_follows = Follow.objects.filter(user=request.user.id)
    authors = []
    for follow in user_follows:
        authors.append(follow.author)
    return authors


class SubscribeView(APIView):
    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        follow = Follow(user=request.user, author=author)
        try:
            follow.full_clean()
            follow.save()
            pass
        except ValidationError_db as e:
            return JsonResponse(
                {"errors": str(e.messages[0])},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserRecipeSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        try:
            follow = Follow.objects.get(user=request.user, author=author)
        except ObjectDoesNotExist:
            return JsonResponse(
                {"errors": UNSUBSCRIBE_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(APIView, LimitOffsetPagination):
    def get(self, request):
        authors = get_follows(request)
        results = self.paginate_queryset(authors, request, view=self)
        serializer = UserRecipeSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)
