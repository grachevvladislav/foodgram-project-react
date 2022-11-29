from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import TagsSerializer, RecipesSerializer
from .models import Tags, Recipes
from .permissions import OwnerOrReadOnly


class TagsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Tags.objects.all()
    lookup_field = 'id'


class RecipesViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = RecipesSerializer
    permission_classes = (OwnerOrReadOnly,)
    queryset = Tags.objects.all()
    lookup_field = 'id'



