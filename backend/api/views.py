from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as ValidationError_db
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import (
    TagsSerializer, RecipeSerializer, IngredientSerializer,
    FavouritesSerializer
)
from .models import Tag, Recipe, Ingredient, Favourites
from .permissions import OwnerOrReadOnly
from users.models import User

UNFAVORIT_ERROR = 'Этого рецепта нет в избранных!'


class TagsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    lookup_field = 'id'


class RecipesViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    queryset = Recipe.objects.all()
    lookup_field = 'id'


class IngredientViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (OwnerOrReadOnly,)
    queryset = Ingredient.objects.all()
    lookup_field = 'id'


class FavouritesView(APIView):
    def post(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        follow = Favourites(user=request.user, recipes=recipe)
        try:
            follow.full_clean()
            follow.save()
            pass
        except ValidationError_db as e:
            return JsonResponse(
                {"errors": str(e.messages[0])},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FavouritesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        try:
            follow = Favourites.objects.get(user=request.user, recipes=recipe)
        except ObjectDoesNotExist:
            return JsonResponse(
                {"errors": UNFAVORIT_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
