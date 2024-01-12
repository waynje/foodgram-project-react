from urllib.parse import unquote

from django_filters.filters import CharFilter
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(carts__user=self.request.user)
        return queryset


class DecodedCharFilter(CharFilter):
    def filter(self, qs, value):
        if value:
            decoded_value = unquote(value)
            return super().filter(qs, decoded_value)
        return qs


class IngredientFilter(FilterSet):
    name = DecodedCharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
