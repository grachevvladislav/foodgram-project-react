from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import TagsSerializer, RecipeSerializer
from .models import Tag, Recipe
from .permissions import OwnerOrReadOnly


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



