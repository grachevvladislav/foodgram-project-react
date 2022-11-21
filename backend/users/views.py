from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from .permissions import IsAdmin
from .serializers import LoginSerializer, MeUserSerializer, UserSerializer

WRONG_DATA = 'Неправильный email или пароль!'


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    queryset = User.objects.all()
    lookup_field = 'id'


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, email=serializer.data['email'])
    if check_password(serializer.data['password'], user.password):
        token = AccessToken.for_user(user)
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
    pass
