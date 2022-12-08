from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagsViewSet, RecipesViewSet, IngredientViewSet,
    FavouritesView,
)

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(
        'recipes/<int:id>/favorite/',
        FavouritesView.as_view(),
        name='favorite'
    ),
    path('', include(router.urls)),
]
