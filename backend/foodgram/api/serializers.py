# from drf_base64.fields import Base64ImageField
from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    CharField,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    ValidationError,
    SerializerMethodField,
)
from rest_framework.validators import (
    UniqueTogetherValidator,
)

from .utils import (
    Base64ImageField
)
from recipes.models import (
    Tags,
    Recipe,
    Ingredient,
    RecipeIngredients,
    Shopping_cart,
    Favorite
)


class TagsSerializer(ModelSerializer):
    # Сериализатор для модели тега, метод GET
    class Meta:
        model = Tags
        exclude = ['id']


class IngredientSerializer(ModelSerializer):
    # Сериализатор для модели ингредиента, метод GET
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientGetSerializer(ModelSerializer):
    # Получение информации об ингредиенте, метод GET
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
        fields = ('__all__')


class IngredientPostSerializer(ModelSerializer):
    # Добавление ингредиента в рецепт, метод POST
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeGetSerializer(ModelSerializer):
    # Получение информации о рецепте с ингредиентами, метод GET
    # author =  Добавить после сериализатора
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
        fields = ('__all__')

    def get_is_favorited(self, obj):
        # Определяем, добавлен ли данный рецепт в избранное
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        # Определяем, добавлен ли данный рецепт в корзину
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Shopping_cart.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class RecipePostSerializer(ModelSerializer):
    # Работа с рецептом, методы POST, PATCH, DELETE
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tags.objects.all()
    )
    # author = Добавить после сериализатора
    ingredients = IngredientPostSerializer(
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients',
            'tags', 'image',
            'name', 'text',
            'cooking_time',
            'author',
        )

    def validate(self, obj):
        # Проверка данных, принятых сериализатором.
        if 'tags' not in obj:
            raise ValidationError(
                'Нужно указать хотя бы 1 тег.'
            )
        if 'ingredients' not in obj:
            raise ValidationError(
                'Нужно указать хотя бы 1 ингредиент.'
            )


class FavoriteSerializer(ModelSerializer):
    # Сериализатор для избранных рецептов
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


class ShoppingCartSerializer(ModelSerializer):
    # Сериализатор для корзины
    class Meta:
        model = Shopping_cart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Shopping_cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]
