import io

from django.db.models import CharField, F, Sum, Value
from django.db.models.functions import Concat
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.tables import Table, TableStyle, colors
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from itertools import chain

from users.models import User
from .mixins import SaveMixin
from .models import Favourite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import OwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSmallSerializer, TagsSerializer)

CANT_DEL_FAVOURIT = 'Этого рецепта нет в Избранных!'
CANT_DEL_CART = 'Этого рецепта нет в Списке покупок!'
CANT_CREATE_FAVOURIT = 'Этот рецепт уже есть в Избранных!'
CANT_CREATE_CART = 'Этот рецепт уже есть в Списке покупок!'


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
            user_favorit = Favourite.objects.filter(user=self.request.user)
            if is_favorited == '1':
                queryset = queryset.filter(
                    id__in=user_favorit.values_list('recipes', flat=True)
                )
            if is_favorited == '0':
                queryset = queryset.exclude(
                    id__in=user_favorit.values_list('recipes', flat=True)
                )
        if is_in_shopping_cart:
            shopping_cart = ShoppingCart.objects.filter(
                user=self.request.user
            )
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    id__in=shopping_cart.values_list('recipes', flat=True)
                )
            if is_in_shopping_cart == '0':
                queryset = queryset.exclude(
                    id__in=shopping_cart.values_list('recipes', flat=True)
                )
        if author:
            author_db = get_object_or_404(User, id=author)
            queryset = queryset.filter(author=author_db)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset


class IngredientViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = chain(
                queryset.filter(name__startswith=name),
                queryset.filter(
                    name__contains=name
                ).exclude(
                    name__startswith=name
                )
            )

        return queryset


class FavouritesView(SaveMixin, APIView):
    permission_classes = [OwnerOrReadOnly]

    def post(self, request, **kwargs):
        return super().post(
            Favourite, RecipeSmallSerializer, CANT_CREATE_FAVOURIT,
            request, **kwargs
        )

    def delete(self, request, **kwargs):
        return super().delete(
            Favourite, CANT_CREATE_FAVOURIT, request, **kwargs
        )


class ShoppingCartView(SaveMixin, APIView):
    permission_classes = [OwnerOrReadOnly]

    def post(self, request, **kwargs):
        return super().post(
            ShoppingCart, RecipeSmallSerializer, CANT_CREATE_CART,
            request, **kwargs
        )

    def delete(self, request, **kwargs):
        return super().delete(
            ShoppingCart, CANT_DEL_CART, request, **kwargs
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    data = [['Название', 'Количество'], ]
    user_shopping_cart = ShoppingCart.objects.filter(user=request.user.id)
    ingredients = Recipe.objects.filter(
        id__in=user_shopping_cart.values('recipes')
    ).values_list(
        'ingredients__ingredient__name'
    ).order_by(
        'ingredients__ingredient__name'
    ).annotate(
        amount=Concat(
            Sum('ingredients__amount'),
            Value(' '),
            F('ingredients__ingredient__measurement_unit'),
            output_field=CharField()
        )
    )
    data += map(list, ingredients)
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
