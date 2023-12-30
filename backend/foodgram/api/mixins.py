from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from recipes.models import Recipe


class ShoppingFavoriteMixin(CreateModelMixin,
                            DestroyModelMixin,
                            GenericViewSet):
    """Миксин для избранного и для корзины."""
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )


class TagsIngredientMixin(ReadOnlyModelViewSet):
    """Миксин для тегов и ингредиентов."""
    permission_classes = (AllowAny,)
    pagination_class = None
