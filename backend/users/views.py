from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as ValidationError_db
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin, CreateModelMixin, RetrieveModelMixin
)
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from django.db import IntegrityError

from .tokens import JWTAccessToken
from .models import User, Follow
from .serializers import (
    LoginSerializer, MeUserSerializer, UserSerializer, PasswordSerializer,
    SubscriptionsSerializer
)
from .pagination import QueryParamPagination


WRONG_DATA = 'Неправильный email или пароль!'
WRONG_PASSWORD = 'Неправильный пароль!'


class UsersViewSet(
    ListModelMixin, CreateModelMixin, RetrieveModelMixin,
    viewsets.GenericViewSet
):
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


class SubscriptionsView(APIView, LimitOffsetPagination):
    def get(self, request):
        print(request.user)
        subscriptions = Follow.objects.all()
        serializer = SubscriptionsSerializer(subscriptions, many=True)
        return Response(serializer.data)

    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs.get('id'))
        follow = Follow(user=request.user, author=author)
        try:
            # follow.full_clean()
            # follow.save()
            pass
        except ValidationError_db as e:
            return JsonResponse(
                {"errors": str(e.messages[0])},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_follows = Follow.objects.filter(user=request.user.id)
        authors = []
        for follow in user_follows:
            authors.append(follow.author)
        results = self.paginate_queryset(authors, request, view=self)
        serializer = SubscriptionsSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

# class SubscriptionsViewSet(generics.CreateAPIView, generics.DestroyAPIView):
#     serializer_class = SubscriptionsSerializer
#     permission_classes = (IsAuthenticated,)
#     pagination_class = QueryParamPagination
#
#     def get_queryset(self):
#         print(self.request.user)
#         return Follow.objects.all()
#
#     def perform_create(self, serializer):
#         author = get_object_or_404(User, id=self.kwargs.get('id'))
#         follow = Follow(user=self.request.user, author=author)
#         follow.save()
