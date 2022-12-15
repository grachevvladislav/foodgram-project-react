from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .models import Recipe
from .serializers import RecipeSmallSerializer


class SaveMixin:
    def post(self, model, serializer, message, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        _, created = model.objects.get_or_create(
            user=request.user, recipes=recipe
        )
        if created:
            serializer = RecipeSmallSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(
            {"errors": message},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, model, message, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('id'))
        try:
            follow = model.objects.get(
                user=request.user,
                recipes=recipe
            )
        except model.DoesNotExist:
            return JsonResponse(
                {"errors": message},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
