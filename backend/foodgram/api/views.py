from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, Shoppingcart,
                            Subscription, Tag, RecipeIngredients)
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .mixins import TagsIngredientMixin
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          TagsSerializer, ShoppingCartSerializer,
                          UserSubscriptionSerializer,
                          UserSubscriptionsGetSerializer)


class TagsViewSet(TagsIngredientMixin):

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientViewSet(TagsIngredientMixin):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filters_backend = (DjangoFilterBackend,)


class RecipeViewSet(ModelViewSet):

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

    @staticmethod
    def create_model_instance(request, instance, serializer_name):
        serializer = serializer_name(
            data={'user': request.user.id, 'recipe': instance.id, },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_model_instance(request, model, instance, error_message):
        if not model.objects.filter(user=request.user,
                                    recipe=instance).exists():
            return Response({'errors': error_message},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(user=request.user, recipe=instance).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        url_name='favorite',
        url_path='favorite'
    )
    def add_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return RecipeViewSet.create_model_instance(
            request,
            recipe,
            FavoriteSerializer
        )

    @add_favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        error_message = 'У вас нет этого рецепта в избранном'
        return RecipeViewSet.delete_model_instance(
            request,
            Favorite,
            recipe,
            error_message
        )

    @action(
        detail=True,
        methods=('POST',),
        url_name='shopping_cart',
        url_path='shopping_cart'
    )
    def add_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return RecipeViewSet.create_model_instance(
            request,
            recipe,
            ShoppingCartSerializer
        )

    @add_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        error_message = 'У вас нет этого рецепта в списке покупок'
        return RecipeViewSet.delete_model_instance(
            request,
            Shoppingcart,
            recipe,
            error_message
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):

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
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response


class UserViewSet(BaseUserViewSet):

    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        methods=('POST',),
        detail=True,
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def add_subscribe(self, request, id=None):
        serializer = UserSubscriptionSerializer(
            data={
                'user': self.request.user.id,
                'author': self.get_object().id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        following = get_object_or_404(User, id=id)
        if not Subscription.objects.filter(user=request.user,
                                           author=following).exists():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(
            user=request.user.id,
            author=following.id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('GET',),
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            UserSubscriptionsGetSerializer(
                self.paginate_queryset(
                    User.objects.filter(
                        following__user=self.request.user
                    ),
                ),
                many=True,
                context={'request': request}
            ).data
        )
