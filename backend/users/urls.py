from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

from .views import (
    UsersViewSet, SubscriptionsView,
    get_token_view, del_token_view,
    me_view, set_password, SubscribeView
)

router = DefaultRouter()
router.register('', UsersViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/login/', get_token_view, name='create_token'),
    path('api/auth/token/logout/', del_token_view, name='del_token'),
    path('api/users/me/', me_view, name='me'),
    path('api/users/set_password/', set_password, name='set_password'),
    path(
        'api/users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    path(
        'api/users/subscriptions/',
        SubscriptionsView.as_view(),
        name='subscriptions'
    ),
    path('api/users/', include(router.urls)),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
