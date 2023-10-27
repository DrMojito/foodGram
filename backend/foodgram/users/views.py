from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from recipes.models import Recipe
from .models import Subscribe
from .pagination import CustomPagination
from users.serializers import (RecipeShortSerializer,
                               CustomUsersSerializer,
                               CustomUsersCreateSerializer,
                               SubscriptionShowSerializers)

User = get_user_model()


class CustomUserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUsersCreateSerializer
    pagination_class = CustomPagination

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        """Сменить пароль."""
        user = request.user
        current_password = request.data.get('current_password', None)
        new_password = request.data.get('new_password', None)

        if not current_password or not new_password:
            return Response(
                {'detail': 'current_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'detail': 'Incorrect current password.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = CustomUsersSerializer(request.user,
                                           context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        """Подписаться или отписаться от автора."""
        author = self.get_object()

        if request.method == 'POST':
            subscription, created = Subscribe.objects.get_or_create(
                user=request.user, author=author)
            if created:
                user_serializer = CustomUsersSerializer(
                    author, context={'request': request})
                recipes_serializer = RecipeShortSerializer(
                    Recipe.objects.filter(author=author), many=True)
                recipes_count = Recipe.objects.filter(author=author).count()
                response_data = {
                    **user_serializer.data,
                    'is_subscribed': True,
                    'recipes': recipes_serializer.data,
                    'recipes_count': recipes_count
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Подписка уже оформлена"},
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscribe, user=request.user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def user_recipes(self, request, pk=None):
        """Извлекать рецепты пользователя."""
        user = self.get_object()
        recipes = Recipe.objects.filter(author=user)
        recipe_serializer = RecipeShortSerializer(recipes, many=True)
        return Response(recipe_serializer.data)

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionShowSerializers,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        """Получить страницу подписок."""
        user = self.request.user
        user_subscriptions = user.subscriber.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)

        return self.get_paginated_response(serializer.data)
