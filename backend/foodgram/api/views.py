from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    GenericViewSet
)
from rest_framework.permissions import (
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin
)
from rest_framework.status import status

from .filters import (
    IngredientFilter,
    RecipeFilter,
)
from .serializers import (
    TagsSerializer,
    RecipeGetSerializer,
    ShortRecipeGetSerializer,
    RecipePostSerializer,
    IngredientGetSerializer,
    IngredientPostSerializer,
    IngredientSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer,
    UserCreateSerializer,
    UserGetSerializer,
    UserSubscriptionSerializer,
    UserSubscriptionsGetSerializer
)
from .permissions import (
    IsAdminAuthorOrReadOnly
)
from .mixins import (
    TagsIngredientMixin,
    ShoppingFavoriteMixin
)
from recipes.models import (
    Tags,
    Recipe,
    RecipeIngredients,
    Ingredient,
    Shoppingcart,
    Favorite,
)
from users.models import (
    User,
    Subscription
)


class TagsViewSet(TagsIngredientMixin):
    # Получение информации о тегах
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class IngredientViewSet(TagsIngredientMixin):
    # Получение информации об ингредиентах
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filters_backend = (DjangoFilterBackend,)


class RecipeViewSet(ModelViewSet):
    # Получение информации о рецептах
    queryset = Recipe.object.all()
    filterset_class = RecipeFilter
    filters_backend = (DjangoFilterBackend,)
    permission_classes = [IsAdminAuthorOrReadOnly,]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer


class UserSubscriptionViewSet(ListModelMixin,
                              GenericViewSet):
    # Получение информации о подписках пользователя
    serializer_class = UserSubscriptionsGetSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class ShoppingCartViewSet(ShoppingFavoriteMixin):
    # Получение информации о списке покупок
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user.id
        return Shoppingcart.objects.filter(user=user)

    def delete(self, request, recipe_id):
        user = request.user
        if not user.shoppingcart.select_related(
                'shoppingrecipe').filter(
                    recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепта нет в корзине'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(Shoppingcart,
                          user=request.user,
                          recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(ShoppingFavoriteMixin):
    # Получение информации об избранных рецептах
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user.id
        return Favorite.objects.filter(user=user)

    def delete(self, request, recipe_id):
        user = request.user
        if not user.favorite.select_related(
                'shoppingrecipe').filter(
                    recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепта нет в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(Favorite,
                          user=request.user,
                          recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
