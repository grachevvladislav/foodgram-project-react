from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagsViewSet, RecipesViewSet

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
