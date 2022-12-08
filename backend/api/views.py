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
from rest_framework.decorators import api_view, permission_classes

from .serializers import (
    TagsSerializer, RecipeSerializer, IngredientSerializer,
    RecipeSmallSerializer
)
from .models import Tag, Recipe, Ingredient, Favourites, Shopping_cart
from .permissions import OwnerOrReadOnly

import io
from django.http import FileResponse
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.tables import TableStyle, colors

from reportlab.platypus.tables import Table
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



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
            follow = Shopping_cart.objects.get(user=request.user, recipes=recipe)
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
    buffer = io.BytesIO()
    my_data = [['ID', 'Name', 'Class', 'Mark', 'Gender'],
               (1, 'John Deo', 'Four', 75, 'female'),
               (2, 'Max Ruin', 'Three', 85, 'male'),
               (3, 'Arnold', 'Three', 55, 'male')]

    my_doc = SimpleDocTemplate(buffer, pagesize=A4)
    c_width = [0.4 * inch, 1.5 * inch, 1 * inch, 1 * inch, 1 * inch]
    table = Table(my_data, rowHeights=20, repeatRows=1, colWidths=c_width)
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('FONTSIZE', (0, 0), (-1, -1), 10)
            ]
        )
    )
    text = 'Список покупок пользователя ' + request.user.username
    styles = getSampleStyleSheet()
    my_doc.build([Paragraph(text, styles['Justify']), table])
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=text + '.pdf')
