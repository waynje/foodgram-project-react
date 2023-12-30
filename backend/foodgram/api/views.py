from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet

from recipes.models import (Favorite, Ingredient, Recipe, Shoppingcart,
                            Subscription, Tag)
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .mixins import ShoppingFavoriteMixin, TagsIngredientMixin
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, TagsSerializer,
                          UserSubscriptionSerializer,
                          UserSubscriptionsGetSerializer)
from .utils import create_model_instance, delete_model_instance


class TagsViewSet(TagsIngredientMixin):
    """Получение информации о тегах."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientViewSet(TagsIngredientMixin):
    """Получение информации об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filters_backend = (DjangoFilterBackend,)


class RecipeViewSet(ModelViewSet):
    """Получение информации о рецептах."""
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filters_backend = (DjangoFilterBackend,)
    permission_classes = [IsAdminAuthorOrReadOnly, ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe, FavoriteSerializer)
        error_message = 'У вас нет этого рецепта в избранном'
        return delete_model_instance(request, Favorite,
                                     recipe, error_message)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """Работа со списком покупок.
        Удаление/добавление в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return create_model_instance(request, recipe,
                                         ShoppingCartSerializer)
        error_message = 'У вас нет этого рецепта в списке покупок'
        return delete_model_instance(request, Shoppingcart,
                                     recipe, error_message)


class ShoppingCartViewSet(ShoppingFavoriteMixin):
    """Получение информации о списке покупок."""
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user.id
        return Shoppingcart.objects.filter(user=user)


class FavoriteViewSet(ShoppingFavoriteMixin):
    """Получение информации об избранных рецептах."""
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user.id
        return Favorite.objects.filter(user=user)


class UserSubscriptionViewSet(ListModelMixin,
                              GenericViewSet):
    """Получение информации о подписках пользователя."""
    serializer_class = UserSubscriptionsGetSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscriptionViewSet(ViewSet):
    """Работа с подписками."""
    serializer_class = UserSubscriptionSerializer

    def get_user(self, pk):
        return get_object_or_404(User, id=pk)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            url_name='list_subscriptions')
    def list_subscriptions(self, request):
        queryset = Subscription.objects.filter(
            user=request.user).order_by('-pk')
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset,
                                         context={'request': request},
                                         many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='subscribe',
            url_name='subscribe')
    def subscribe(self, request, pk=None):
        target_user = self.get_user(pk)
        serializer = UserSubscriptionSerializer(
            data={'author': target_user.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save(user=request.user)
        return Response(UserSubscriptionSerializer(
            subscription,
            context={'request': request}).data,
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='subscribe',
            url_name='unsubscribe')
    def unsubscribe(self, request, pk=None):
        target_user = self.get_user(pk)
        serializer = UserSubscriptionSerializer(
            data={'author': target_user.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = Subscription.objects.get(
            user=request.user, author=target_user)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
