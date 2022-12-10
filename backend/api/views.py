import io

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as ValidationError_db
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.tables import Table, TableStyle, colors
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User

from .models import Favourites, Ingredient, Recipe, Shopping_cart, Tag
from .permissions import OwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSmallSerializer, TagsSerializer)

UNFAVORIT_ERROR = 'Этого рецепта нет в избранных!'


class TagsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    lookup_field = 'id'


class RecipesViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        if is_favorited:
            favorit = Favourites.objects.filter(user=self.request.user)
            favorit_recipe_id = []
            for recipe in favorit:
                favorit_recipe_id.append(recipe.recipes.id)
            if is_favorited == '1':
                queryset = queryset.filter(id__in=favorit_recipe_id)
            if is_favorited == '0':
                queryset = queryset.exclude(id__in=favorit_recipe_id)
        if is_in_shopping_cart:
            shopping_cart = Shopping_cart.objects.filter(
                user=self.request.user
            )
            shopping_cart_recipe_id = []
            for recipe in shopping_cart:
                shopping_cart_recipe_id.append(recipe.recipes.id)
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(id__in=shopping_cart_recipe_id)
            if is_in_shopping_cart == '0':
                queryset = queryset.exclude(id__in=shopping_cart_recipe_id)
        if author:
            author_db = get_object_or_404(User, id=author)
            queryset = queryset.filter(author=author_db)
        if tags:
            for tag in tags:
                tag_db = get_object_or_404(Tag, slug=tag)
                queryset = queryset.filter(tags=tag_db)
        return queryset


class IngredientViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)


class FavouritesView(APIView):
    permission_classes = [OwnerOrReadOnly]

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
        serializer = RecipeSmallSerializer(recipe)
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


class ShoppingCartView(APIView):
    permission_classes = [OwnerOrReadOnly]

    def post(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        follow = Shopping_cart(user=request.user, recipes=recipe)
        try:
            follow.full_clean()
            follow.save()
            pass
        except ValidationError_db as e:
            return JsonResponse(
                {"errors": str(e.messages[0])},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = RecipeSmallSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        try:
            follow = Shopping_cart.objects.get(
                user=request.user,
                recipes=recipe
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"errors": UNFAVORIT_ERROR},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    data = [['Название', 'Количество'],]
    user_shopping_cart = Shopping_cart.objects.filter(user=request.user.id)
    ingredients_dict = {}
    for recipe in user_shopping_cart:
        for ingredient in recipe.recipes.ingredients.all():
            if ingredient.ingredient.id in ingredients_dict:
                ingredients_dict[ingredient.ingredient.id] = [
                    ingredient.ingredient.name,
                    ingredient.amount + ingredients_dict[
                        ingredient.ingredient.id
                    ][1],
                    ingredient.ingredient.measurement_unit
                ]
            else:
                ingredients_dict[ingredient.ingredient.id] = [
                    ingredient.ingredient.name,
                    ingredient.amount,
                    ingredient.ingredient.measurement_unit
                ]
    for key, value in ingredients_dict.items():
        data.append([value[0], f'{value[1]} {value[2]}'])
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    c_width = [4 * inch, 3 * inch]
    text = 'Список покупок пользователя ' + request.user.username
    styles = getSampleStyleSheet()
    pdfmetrics.registerFont(
        TTFont('timesnewromanpsmt', 'api/timesnewromanpsmt.ttf')
    )
    styles['Title'].fontName = 'timesnewromanpsmt'
    table = Table(data, rowHeights=20, repeatRows=1, colWidths=c_width)
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('FONTNAME', (0, 0), (-1, -1), 'timesnewromanpsmt'),
                ('FONTSIZE', (0, 0), (-1, -1), 10)
            ]
        )
    )
    doc.build([Paragraph(text, styles['Title']), table])
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=text + '.pdf')
