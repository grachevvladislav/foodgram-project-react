from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UsersViewSet,  # create_user_view, token_view,
                    get_token_view, me_view, set_password)

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', get_token_view, name='token'),
    path('users/me/', me_view, name='me'),
    path('users/set_password/', set_password, name='set_password'),
    path('', include(router.urls)),
]
