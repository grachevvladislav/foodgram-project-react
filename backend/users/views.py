from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as ValidationError_db
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow, User
from .permissions import IsSafeOrPost
from .serializers import (LoginSerializer, PasswordSerializer,
                          UserPostSerializer, UserRecipeSerializer,
                          UserSerializer)
from .tokens import JWTAccessToken

WRONG_DATA = 'Неправильный email или пароль!'
WRONG_PASSWORD = 'Неправильный пароль!'
CANT_DEL_SUBSCRIBE = 'Этого автора нет в Подписках!'
CANT_CREATE_SUBSCRIBE = 'Этот автор уже есть в Подписках!'


class UsersViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsSafeOrPost,)
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
    user = get_object_or_404(User, email=serializer.validated_data['email'])
    if check_password(serializer.validated_data['password'], user.password):
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
        serializer.validated_data['current_password'],
        request.user.password
    ):
        request.user.set_password(serializer.validated_data['new_password'])
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
    return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        _, created = Follow(user=request.user, author=author)
        if created:
            serializer = UserRecipeSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            {"errors": CANT_CREATE_SUBSCRIBE},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        try:
            follow = Follow.objects.get(user=request.user, author=author)
        except Follow.DoesNotExist:
            return JsonResponse(
                {"errors": CANT_DEL_SUBSCRIBE},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(APIView, LimitOffsetPagination):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_subscribes = Follow.objects.filter(user=request.user)
        authors = User.objects.filter(
            id__in=user_subscribes.values_list('author__id', flat=True)
        )
        results = self.paginate_queryset(authors, request, view=self)
        serializer = UserRecipeSerializer(
            results,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
