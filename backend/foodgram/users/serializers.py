from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import Subscribe
from recipes.models import Recipe
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUsersCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'password')


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class CustomUsersSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if "request" not in self.context:
            return False
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user.id,
            author=obj.id,
        ).exists()

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'is_subscribed')


class SubscriptionShowSerializers(CustomUsersSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj).all()
        if limit:
            recipes = recipes[:(int(limit))]
        srs = RecipeShortSerializer(recipes, many=True,
                                    context={'request': request})
        return srs.data

    class Meta(CustomUsersSerializer.Meta):
        fields = CustomUsersSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )


class SubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj)

        if 'recipes_limit' in self.context['request'].GET:
            recipes_limit = self.context['request'].GET['recipes_limit']
            author_recipes = author_recipes[:int(recipes_limit)]

        if author_recipes:
            serializer = RecipeShortSerializer(
                author_recipes, context={'request': self.context['request']},
                many=True)
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = Subscribe
        fields = "__all__"


class AuthorRecipesSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        author_recipes = Recipe.objects.filter(author=obj)

        if 'recipes_limit' in self.context.get('request').GET:
            recipes_limit = self.context.get('request').GET['recipes_limit']
            author_recipes = author_recipes[:int(recipes_limit)]

        return RecipeShortSerializer(author_recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'bio', 'role', 'confirmation_code', 'author',
                  'recipes', 'recipes_count')
