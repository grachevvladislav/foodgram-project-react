from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UsersViewSet,  # create_user_view, token_view,
                    get_token_view, del_token_view, me_view, set_password)

router = DefaultRouter()
router.register('', UsersViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/login/', get_token_view, name='create_token'),
    path('api/auth/token/logout/', del_token_view, name='del_token'),
    path('api/users/me/', me_view, name='me'),
    path('api/users/set_password/', set_password, name='set_password'),
    path('api/users', include(router.urls)),
]
