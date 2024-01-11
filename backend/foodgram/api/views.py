from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, Shoppingcart,
                            Subscription, Tag, RecipeIngredients)
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .mixins import TagsIngredientMixin
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

    def _check_model_entry(self, model, user, recipe, method):
        """Private method for ADD/DELETE recipe to favorite/shopping cart."""
        entry_exists = model.objects.filter(recipe=recipe, user=user).exists()

        if method == 'POST' and not entry_exists:
            model.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif method == 'DELETE' and entry_exists:
            model.objects.filter(recipe=recipe, user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            if entry_exists:
                error_message = 'Рецепт уже добавлен!'
            else:
                error_message = 'Рецепт уже удален!'
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
    )
    def favorite(self, request, pk):
        return self._check_model_entry(
            Favorite,
            user=get_object_or_404(User, id=self.request.user.id),
            recipe=get_object_or_404(Recipe, id=pk),
            method=request.method
        )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
    )
    def shopping_cart(self, request, pk):
        return self._check_model_entry(
            Shoppingcart,
            user=get_object_or_404(User, id=self.request.user.id),
            recipe=get_object_or_404(Recipe, id=pk),
            method=request.method)
    
    
    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated, ]
    # )
    # def favorite(self, request, pk):
    #     """Работа с избранными рецептами.
    #     Удаление/добавление в избранное."""
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     if request.method == 'POST':
    #         return create_model_instance(request, recipe, FavoriteSerializer)
    #     error_message = 'У вас нет этого рецепта в избранном'
    #     return delete_model_instance(request, Favorite,
    #                                  recipe, error_message)

    # @action(
    #     detail=True,
    #     methods=['post', 'delete'],
    #     permission_classes=[IsAuthenticated, ]
    # )
    # def shopping_cart(self, request, pk):
    #     """Работа со списком покупок.
    #     Удаление/добавление в список покупок."""
    #     recipe = get_object_or_404(Recipe, id=pk)
    #     if request.method == 'POST':
    #         return create_model_instance(request, recipe,
    #                                      ShoppingCartSerializer)
    #     error_message = 'У вас нет этого рецепта в списке покупок'
    #     return delete_model_instance(request, Shoppingcart,
    #                                  recipe, error_message)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = RecipeIngredients.objects.filter(
            recipe__shoppingrecipe__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class UserSubscriptionViewSet(ListModelMixin,
                              GenericViewSet):
    """Получение информации о подписках пользователя."""
    serializer_class = UserSubscriptionsGetSerializer

    def get_queryset(self, request):
        queryset = User.objects.filter(following__follower=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscriptionsGetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriptionsGetSerializer(queryset, many=True)
        return Response(serializer.data)


class UserSubscribeView(APIView):
    """Создание/удаление подписки на пользователя."""
    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = UserSubscriptionSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(user=request.user,
                                           author=author).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(user=request.user.id,
                                 author=user_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
