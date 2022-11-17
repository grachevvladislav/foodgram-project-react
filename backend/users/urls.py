from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    me_view, UsersViewSet,
    # create_user_view, token_view,
)


router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')

# auth = [
#     path('auth/signup/', create_user_view, name='signup'),
#     path('auth/token/', token_view, name='token'),
# ]
urlpatterns = [
    #path('users/me/', me_view),
    #path('users/', include(auth)),
    path('', include(router.urls)),
]
