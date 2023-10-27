from rest_framework import viewsets, exceptions, status
from .models import Recipe, Favorite, ShoppingCart, RecipeIngredients
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnlyPermission
from users.pagination import CustomPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from .serializers import RecipeCreateUpdateSerializer,  RecipeSerializer
from users.serializers import RecipeShortSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter
from django.db.models import Sum


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnlyPermission]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if self.request.method == 'POST':
            if Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError('Рецепт уже в избранном.')

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe,
                context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    'Рецепта нет в избранном, либо он уже удален.'
                )

            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'])
    def shopping_cart(self, request, pk):
        """Способ добавления/удаления рецепта из корзины покупок."""
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_from(ShoppingCart, request.user, pk)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def add_to(self, model, user, pk):
        """Метод добавления рецепьа в корзину."""
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в корзину покупок!'},
                status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        """Метод удаления рецепта из корзины покупок."""
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепта нет в корзине покупок или он уже был удален!'},
            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        shopping_carts = ShoppingCart.objects.filter(user=user)

        if not shopping_carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        filename = 'ingredients.txt'
        ingredients = (
            RecipeIngredients.objects
            .filter(recipe__in=shopping_carts.values_list('recipe', flat=True))
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(Sum('amount'))
        )

        text_data = ""
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['amount__sum']
            text_data += f'{name}: {amount} {unit}\n'

        response = HttpResponse(content_type="text/plain")
        response['Content-Disposition'] = f'attachment; filename={filename}'
        response.write(text_data)
        return response
