import re

from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            Shoppingcart, Subscription, Tag)
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator

from users.models import User
from .utils import Base64ImageField


class ShortRecipeGetSerializer(ModelSerializer):
    """Получение краткой информации о рецепте (в избранном и корзине)."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserCreateSerializer(UserCreateSerializer):
    """Создание юзера через djoser."""
    class Meta:
        model = User
        fields = '__all__'

    def validate_username(self, username):
        if username.lower() == 'me':
            raise ValidationError('Недопустимый username.')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise ValidationError('Недопустимые символы.')
        return username


class UserGetSerializer(UserSerializer):
    """Получение информации о пользователе, метод GET."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'is_subscribed', 'id',
                  'username', 'email',
                  )

    def get_is_subscribed(self, object):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user,
                                           author=object).exists()


class UserSubscriptionSerializer(ModelSerializer):
    """Подписка на пользователя, метод POST."""
    class Meta:
        model = Subscription
        fields = '__all__'
        validator = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного пользователя.'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user != data['author']:
            return data
        raise ValidationError('Нельзя подписаться на самого себя.')


class TagsSerializer(ModelSerializer):
    """Сериализатор для модели тега, метод GET."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатор для модели ингредиента, метод GET."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientGetSerializer(ModelSerializer):
    """Получение информации об ингредиенте, метод GET."""
    id = ReadOnlyField(
        source='ingredient.id',
    )
    name = ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class RecipeIngredientsSerializer(ModelSerializer):
    """Serializer for amount of ingredinets in recipe."""
    name = CharField(source='ingredient.name',
                     read_only=True)
    measurement_unit = CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(ModelSerializer):
    """Получение информации о рецепте с ингредиентами, метод GET."""
    author = UserGetSerializer(read_only=True)
    tags = TagsSerializer(
        many=True,
        read_only=True,
    )
    ingredients = IngredientGetSerializer(
        many=True,
        read_only=True,
        source='recipeingredients',
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        """Определяем, добавлен ли данный рецепт в избранное."""
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        """Определяем, добавлен ли данный рецепт в корзину."""
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Shoppingcart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipePostSerializer(ModelSerializer):
    """Работа с рецептом, методы POST, PATCH, DELETE."""
    author = UserGetSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeingredients',
        read_only=True
    )
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients',
            'tags', 'image',
            'name', 'text',
            'cooking_time',
            'author',
        )

    def create_ingredients(self, ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredient,
                                                   id=ingredient.get('id'))
            amount = ingredient.get('amount')
            ingredient_list.append(RecipeIngredients(
                                   recipe=recipe,
                                   ingredient=current_ingredient,
                                   amount=amount))
        RecipeIngredients.objects.bulk_create(ingredient_list)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = self.initial_data.pop('ingredients')
        tags_ids = self.initial_data.get('tags')
        tags = Tag.objects.filter(id__in=tags_ids)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        instance.save()
        super().update(instance, validated_data)
        return instance


class FavoriteSerializer(ModelSerializer):
    """Сериализатор для избранных рецептов."""
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeGetSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class ShoppingCartSerializer(ModelSerializer):
    """Сериализатор для корзины."""
    class Meta:
        model = Shoppingcart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Shoppingcart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeGetSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class UserSubscriptionsGetSerializer(UserGetSerializer):
    recipes = RecipeGetSerializer(read_only=True, many=True)
    recipes_count = ReadOnlyField(
        source='recipes.count',
        read_only=True
    )

    class Meta(UserGetSerializer.Meta):
        fields = UserGetSerializer.Meta.fields + ('recipes', 'recipes_count')
